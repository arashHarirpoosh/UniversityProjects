import time
from coapthon.client.helperclient import HelperClient
from peewee import *


host = "192.168.43.113"
port = 5683
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
def get_user_requirements(user_id):
    rows = UserRequirements.select().where(UserRequirements.id == user_id)
    if len(rows) > 0:
        return True, rows[0].waterLevel, rows[0].heatLevel
    else:
        return False, 0, 0


def main():
    manage_data()
    # Handle responses of server that is running in the specified host and port
    client = HelperClient(server=(host, port))
    try:
        while True:
            # Get the ID number that has been read in node1 RFID
            response = client.get('tagID')
            print(response.pretty_print())
            resp = response.payload
            # Check if server received the new ID number of RFID or nor
            if resp is not None:
                # Remove characters that are not number nor alphabets from received response
                getVals = list([val for val in resp if val.isalnum()])
                user_id = "".join(getVals)

                # Reset the ID number in the server so that we understand when the new ID has been send to ther server
                response = client.put('tagID', '')
                print(response.pretty_print())

                status, water_level, heat_level = get_user_requirements(user_id)
                if status:
                    msg = 'WL:' + str(water_level) + ', HL:' + str(heat_level) + ','
                    # Send the user requirements for the server
                    response = client.put('userInfo', msg)
                    print(response.pretty_print())
            time.sleep(5)  # Send data every 5 seconds
    except KeyboardInterrupt:
        print('Client Shutdown')
        client.stop()
        print('Exiting...')


if __name__ == '__main__':
    main()
