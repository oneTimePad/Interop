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


missions,error = client.get_mission().result()
if error != None:
    raise Exception(error)
print missions[0]

"""
TODO: parse the mission information and load it via dronekit
Look in types.py under the 'Mission' object to understand the fields returned

"""
