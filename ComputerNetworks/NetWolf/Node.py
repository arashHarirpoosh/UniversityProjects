import socket
import threading
import time
import os
from os import listdir
from os.path import isfile, join

MESSAGE_LENGTH_SIZE = 64
DISCOVERY_TIME = 20
WAIT_FOR_RESPONSE = 5
MAX_RESPONSE = 3

Encoding = 'utf-8'

class Node:
    def __init__(self, name,  cluster_members, udp_port):
        self.name = name
        self.folder_path = 'nodes_memory\\'+name
        self.num_of_responses = 0
        self.cluster_members = cluster_members
        self.name_rcv_file_before = []
        self.get_response = {}
        self.TCP_Response_Time = {}
        self.tcp_client_connections = {}
        self.lock = threading.RLock()
        self.get_response_lock = threading.RLock()
        self.udp_connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.discovery_update = threading.Thread(target=self.discovery, args=(udp_port, ))
        self.tcp_server = threading.Thread(target=self.start_tcp_connection)
        self.discovery_update.start()
        self.tcp_server.start()

        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)


    def serialized_cluster_members(self):
        all_cluster_members = []
        self.lock.acquire()
        try:
            cluster_members = self.cluster_members
        finally:
            self.lock.release()
        addr = self.udp_connection.getsockname()
        all_cluster_members.append(self.name + ':' + str(addr[0]) + ':' + str(addr[1]) + ':')

        for cn, ca in cluster_members.items():
            all_cluster_members.append(cn + ':' + ca + ':')
        return ''.join(all_cluster_members)

    def discovery(self, port):
        udp_socket = self.udp_connection
        host_information = ('', port)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.settimeout(1.0)
        udp_socket.bind(host_information)
        print("UDP Socket Connected ...", udp_socket.getsockname()[0], ":", port)
        send = threading.Thread(target=self.send_discover, args=(udp_socket, )).start()
        rec = threading.Thread(target=self.listen_discover, args=(udp_socket, )).start()

    def send_discover(self, udp_socket):
        while 1:
            self.lock.acquire()
            try:
                cluster_members_value = self.cluster_members.values()
            finally:
                self.lock.release()

            if len(cluster_members_value) > 0:
                msg = 'Discovery:' + self.serialized_cluster_members()

                for m in list(cluster_members_value):
                    address_parts = m.split(':')
                    host_information = ('<broadcast>', int(address_parts[1]))
                    udp_socket.sendto(msg.encode(Encoding), host_information)

                time.sleep(DISCOVERY_TIME)

    def send_GET_Request(self, file_name):
        udp_socket = self.udp_connection
        self.lock.acquire()
        try:
            cluster_members = self.cluster_members
        finally:
            self.lock.release()
        if len(cluster_members) > 0:
            msg = 'GET:' + file_name
            for k, v in cluster_members.items():

                self.get_response_lock.acquire()
                try:
                    self.get_response[k] = [file_name]
                finally:
                    self.get_response_lock.release()

                address_parts = v.split(':')
                host_information = ('<broadcast>', int(address_parts[1]))
                udp_socket.sendto(msg.encode(Encoding), host_information)
                print("GET Request sent to ", k)
        time.sleep(WAIT_FOR_RESPONSE)
        if len(self.get_response) > 0:
            self.say_hello()
        else:
            print('Sorry The File Doesnt Exist On Online Nodes')

    def find_min_elapsed_time(self):
        return min(self.TCP_Response_Time.items(), key=lambda x: x[1][0])

    def check_the_existence_of_file(self, file_name):
        existed_files = [f for f in listdir(self.folder_path) if isfile(join(self.folder_path, f))]
        for i in existed_files:
            if i == file_name:
                return True
        return False

    def merge_cluster_members(self, data):
        self.lock.acquire()
        try:
            keys = self.cluster_members.keys()
        finally:
            self.lock.release()

        num_of_members = int((len(data) - 1) / 3)
        for i in range(num_of_members):
            base = i*3
            rcv_addr = data[base + 2] + ':' + data[base + 3]
            name = data[base+1]
            if name not in keys and name != self.name:
                self.lock.acquire()
                try:
                    self.cluster_members[name] = rcv_addr
                finally:
                    self.lock.release()

    def listen_discover(self, udp_socket):
        while 1:
            try:
                time.sleep(0.1)
                data, addr = udp_socket.recvfrom(1024)

                data_recv = data.decode(Encoding)
                data_parts = data_recv.split(":")

                if data_parts[0] == 'Discovery':

                    self.merge_cluster_members(data_parts)

                elif data_parts[0] == 'GET':
                    if self.check_the_existence_of_file(data_parts[1]):
                        tcp_address = self.tcp_server_connection.getsockname()
                        get_acc = 'Exist:' + self.name + ':' + data_parts[1] + ':' + tcp_address[0] + ':' + str(tcp_address[1])
                        udp_socket.sendto(get_acc.encode(Encoding), ('<broadcast>', addr[1]))
                elif data_parts[0] == 'Exist':
                    key = data_parts[1]
                    file_name = data_parts[2]
                    key_existed = key in self.get_response.keys()
                    if key_existed and self.get_response[key][0] == file_name:

                        tcp_address = data_parts[3]
                        tcp_port = int(data_parts[4])

                        self.get_response[key].clear()
                        self.get_response[key] = [file_name, tcp_address, tcp_port]
                        print(data_parts)

            except socket.timeout:
                pass

    def say_hello(self):
        addr = self.tcp_server_connection.getsockname()
        msg = 'HELLO:' + self.name + ':' + addr[0] + ':' + str(addr[1])
        message = msg.encode(Encoding)
        tcp_connection_nodes = self.tcp_client_connections.keys()

        receivers = self.get_response
        for k, r in list(receivers.items()):
            receiver_name = k
            try:
                receiver_information = (r[1], r[2])
            except IndexError:
                self.get_response_lock.acquire()
                try:
                    del self.get_response[k]
                finally:
                    self.get_response_lock.release()

                continue

            if receiver_name in tcp_connection_nodes:
                tcp_connection = self.tcp_client_connections[receiver_name]
            else:
                try:
                    tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcp_connection.connect(receiver_information)
                    self.tcp_client_connections[receiver_name] = tcp_connection
                except ConnectionRefusedError:
                    continue

            msg_length = len(message)
            msg_length = str(msg_length).encode(Encoding)
            msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

            self.TCP_Response_Time[receiver_name] = [time.time(), receiver_information]

            try:
                tcp_connection.send(msg_length)
                tcp_connection.send(message)
            except :
                tcp_connection.close()

    def send_file(self, tcp_connection, file_name):
        self.num_of_responses += 1
        addr = self.folder_path + '\\' + file_name
        print(addr)
        with open(addr, 'rb') as file:
            data = file.read(MESSAGE_LENGTH_SIZE)

            print('Sending...', data)
            while data:
                msg_length = min(len(data), MESSAGE_LENGTH_SIZE)
                msg_length = str(msg_length).encode(Encoding)
                msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
                tcp_connection.send(msg_length)
                tcp_connection.send(data)
                print('Sending...')

                data = file.read(MESSAGE_LENGTH_SIZE)

        print("Done Sending")
        response = 'Send Completed'
        self.num_of_responses -= 1
        msg_length = len(response)
        msg_length = str(msg_length).encode(Encoding)
        msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
        tcp_connection.send(msg_length)
        try:
            tcp_connection.send(response.encode(Encoding))
            msg_length = int(tcp_connection.recv(MESSAGE_LENGTH_SIZE).decode(Encoding))
            resp_parts = tcp_connection.recv(msg_length).decode(Encoding).split(':')
            print('File', resp_parts[1], 'Sent Successfully')
        except ConnectionResetError:
            pass

    def receive_file(self, tcp_connection, file_name):
        addr = self.folder_path + '\\' + file_name
        file = open(addr, 'wb')
        try:
            msg_length = tcp_connection.recv(MESSAGE_LENGTH_SIZE)
            msg_length = int(msg_length.decode(Encoding))
            data = tcp_connection.recv(msg_length)
            file.write(data)
            print("Receiving...")
        except ConnectionResetError:
            pass
        while 1:
            try:
                data_length = int(tcp_connection.recv(MESSAGE_LENGTH_SIZE).decode(Encoding))
                data = tcp_connection.recv(data_length)
                print("Receiving...")
            except ConnectionError:
                break
            try:
                if data.decode(Encoding) == 'Send Completed':
                    break
            except UnicodeDecodeError:
                pass
            file.write(data)

        file.close()
        print("Done Receiving")
        response = 'Done:'+ file_name
        msg_length = len(response)
        msg_length = str(msg_length).encode(Encoding)
        msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
        try:
            tcp_connection.send(msg_length)
            tcp_connection.send(response.encode(Encoding))
        except ConnectionResetError:
            pass

    def start_tcp_connection(self):
        tcp_sock = self.tcp_server_connection

        tcp_sock.bind((socket.gethostname(), 0))
        address = tcp_sock.getsockname()[0]
        port = tcp_sock.getsockname()[1]
        tcp_sock.listen()
        while 1:
            print("TCP Socket Connected ... ", address, ":", port)
            conn, address = tcp_sock.accept()
            print('TCP Listened On ', address)

            t = threading.Thread(target=self.handle_client, args=(conn, address))
            t.start()

    def handle_client(self, conn, address):
        print('[new connectin] connected from{}'.format(conn, address))
        connected = True
        while connected:
            try:
                message_length = int(conn.recv(MESSAGE_LENGTH_SIZE).decode(Encoding))
                msg = conn.recv(message_length).decode(Encoding)
            except (ConnectionResetError , OSError):
                print(address, ' closed')

                connected = False
            print('[message recieved] {}'.format(msg))

            data_parts = msg.split(':')
            if data_parts[0] == 'HELLO':
                if self.num_of_responses < MAX_RESPONSE:
                    addr = self.tcp_server_connection.getsockname()
                    response = 'ACKHELLO:' + self.name + ':' + addr[0] + ':' + str(addr[1])
                    receiver_name = data_parts[1]

                    receiver_information = (data_parts[2], int(data_parts[3]))
                    if receiver_name in self.tcp_client_connections.keys():
                        tcp_connection = self.tcp_client_connections[receiver_name]
                    else:
                        tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_connection.connect(receiver_information)
                        self.tcp_client_connections[receiver_name] = tcp_connection
                    msg_length = len(response)
                    msg_length = str(msg_length).encode(Encoding)
                    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

                    # self.TCP_Response_Time[receiver_name] = [time.time(), receiver_information]

                    try:
                        if receiver_name not in self.name_rcv_file_before:
                            time.sleep(1)
                        tcp_connection.send(msg_length)
                        tcp_connection.send(response.encode(Encoding))
                        print('send ', response, tcp_connection.getsockname())
                    except OSError:
                        tcp_connection.close()
                        del self.tcp_client_connections[receiver_name]
                        pass
                else:
                    addr = self.tcp_server_connection.getsockname()
                    response = 'NotResponding:' + self.name + ':' + addr[0] + ':' + str(addr[1])
                    receiver_name = data_parts[1]

                    receiver_information = (data_parts[2], int(data_parts[3]))
                    if receiver_name in self.tcp_client_connections.keys():
                        tcp_connection = self.tcp_client_connections[receiver_name]
                    else:
                        tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        tcp_connection.connect(receiver_information)
                        self.tcp_client_connections[receiver_name] = tcp_connection
                    msg_length = len(response)
                    msg_length = str(msg_length).encode(Encoding)
                    msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))

            elif data_parts[0] == 'NotResponding':
                print(data_parts)
                if data_parts[1] in self.TCP_Response_Time.keys():
                    del self.TCP_Response_Time[data_parts[1]]

            elif data_parts[0] == 'ACKHELLO':
                self.get_response_lock.acquire()
                try:
                    if data_parts[1] in self.TCP_Response_Time.keys() and self.get_response.keys():
                        start_time = self.TCP_Response_Time[data_parts[1]][0]
                        self.TCP_Response_Time[data_parts[1]][0] = time.time() - start_time

                        if len(self.get_response) == 1:
                            sender_info = self.find_min_elapsed_time()
                            print('client choosed', sender_info, type(sender_info))

                            tcp_connection = self.tcp_client_connections[sender_info[0]]
                            file_name = self.get_response[data_parts[1]][0]
                            response = 'SendFile:' + self.name + ':' + file_name
                            msg_length = len(response)
                            msg_length = str(msg_length).encode(Encoding)
                            msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
                            tcp_connection.send(msg_length)
                            tcp_connection.send(response.encode(Encoding))
                            self.TCP_Response_Time.clear()
                        del self.get_response[data_parts[1]]

                finally:
                    self.get_response_lock.release()
            elif data_parts[0] == 'SendFile':
                rcv_name = data_parts[1]
                file_name = data_parts[2]
                info = tcp_connection.getsockname()
                response = 'File:' + self.name + ':' + file_name + ':' + info[0] + ':' + str(info[1])
                msg_length = len(response)
                msg_length = str(msg_length).encode(Encoding)
                msg_length += b' ' * (MESSAGE_LENGTH_SIZE - len(msg_length))
                try:
                    tcp_connection.send(msg_length)
                    tcp_connection.send(response.encode(Encoding))
                    print(self.tcp_client_connections[rcv_name])
                    threading.Thread(target=self.send_file, args=(tcp_connection, file_name)).start()
                except ConnectionResetError:
                    del self.tcp_client_connections[data_parts[1]]
                    pass
                # self.send_file(tcp_connection, file_name)


            elif data_parts[0] == 'File':
                if data_parts[1] not in self.name_rcv_file_before:
                    self.name_rcv_file_before.append(data_parts[1])
                file_name = data_parts[2]
                # threading.Thread(target=self.receive_file, args=(conn, file_name))
                self.receive_file(conn, file_name)

            elif msg == 'Disconnect':
                connected = False

        conn.close()



