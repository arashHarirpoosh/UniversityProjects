from Node import Node
import os
import threading
import time

def terminal(N):
    command = ''
    while command != 'end':
        command = input('command: ')
        command_parts = command.split(' ')
        if command_parts[0] == 'get':
            N.send_GET_Request(command_parts[1])
            time.sleep(7)
        elif command_parts[0] == 'discovery_list':
            print(N.cluster_members)
        elif command == 'end':
            os._exit(1)

if __name__ == '__main__':
    name = input('Name Of The Node: ')
    port = int(input('UDP Port Of The Node: '))
    name_in = ''
    addr_in = ''
    cluster_members={}
    while 1:
        name_in = input('Name Of The Cluster Member: ')
        if name_in == '':
            break
        addr_in = input('Address Of The Cluster Member: ')
        cluster_members[name_in] = addr_in

    Node = Node(name, cluster_members, port)
    # N0 = Node('N0', {}, 7443)
    # N1 = Node('N1', {'N0':'0.0.0.0:7443'}, 7444)
    # N2 = Node('N2', {'N1':'0.0.0.0:7444'}, 7445)
    # N3 = Node('N3', {'N1':'0.0.0.0:7444'}, 7446)
    command = threading.Thread(target=terminal, args=(Node, ))
    command.start()


# get Hello.txt
# discovery_list
