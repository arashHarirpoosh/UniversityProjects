from paho.mqtt import client as mqtt_client
import random
from peewee import *
import time

broker = '192.168.43.113'
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
user_id = None
db = SqliteDatabase('users.db')


class UserRequirements(Model):
    id = TextField(primary_key=True)
    waterLevel = IntegerField()
    heatLevel = IntegerField()

    class Meta:
        database = db
        db_table = 'user_requirements'


# Create Database user_requirements for storing user requirements if it's not exist
# Inserting the Card and Tag ID requirements after creating the database
def manage_data():
    tables = db.get_tables()
    if 'user_requirements' not in tables:
        db.create_tables([UserRequirements])
        rows = [
            # Cart ID
            {'id': 'C9ED40BA', 'waterLevel': 50, 'heatLevel': 10},
            # TAG ID
            {'id': '4C6C3F22', 'waterLevel': 5, 'heatLevel': 50}
                 ]
        q = UserRequirements.insert_many(rows)
        q.execute()


# Read the user requirements from database
def get_user_requirements(received_id):
    rows = UserRequirements.select().where(UserRequirements.id == received_id)
    if len(rows) > 0:
        return True, rows[0].waterLevel, rows[0].heatLevel
    else:
        return False, 0, 0


# Connect to the mqtt broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


# Publish User requirements in inTopic based on Received tag ID
def publish(client, topic):
    global user_id

    while True:
        status, water_level, heat_level = get_user_requirements(user_id)
        if status:
            pub_msg = 'WL:' + str(water_level) + ', HL:' + str(heat_level) + ','
            result = client.publish(topic, pub_msg)
            status = result[0]
            if status == 0:
                print(f"Send `{pub_msg}` to topic `{topic}`")
                user_id = None
            else:
                print(f"Failed to send message to topic {topic}")


# Subscribe to the outTopic to receive Tag ID
def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        global user_id
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        user_id = str(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message


# Run the MQTT Client by
#   Connecting to the MQTT broker
#   Subscribing to the outTopic to receive tagID, and
#   Publish user requirements in inTopic based on the received tagID
def run():
    manage_data()
    client = connect_mqtt()
    client.loop_start()
    subscribe(client, topic="tagID")
    publish(client, topic="userInfo")


if __name__ == '__main__':
    run()
