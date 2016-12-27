from interop import Client
import binascii
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("url",help="url for django server (http://ip:port)",type=str)
parser.add_argument("username",help="username for django server",type=str)
parser.add_argument("password",help="password for django server",type=str)

args = parser.parse_args()
#pdb.set_trace()
url = args.url
username = args.username
password = args.password


while True:
    try:
        client = Client(url,username,password)
        break
    except (TypeError, binascii.Error):
        continue


moving,stationary,error = client.get_obstacles().result()

if error != None:
    raise Exception(error)
"""
#TODO: add the rest of sda
moving is a list of MovingObstacle objects
stationary is a list of StationaryObstacle objects
look in types.py for these objects
"""
print moving
print stationary
