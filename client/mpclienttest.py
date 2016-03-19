import xmlrpclib
from time import sleep

try:
    server = xmlrpclib.ServerProxy('http://127.0.0.1:9000')
    lat = 0
    while True:
            server.telemetry(float(lat),float(14),float(15),float(16))
            print("Sent telemetry.")
            lat+=1
            sleep(1)
except IOError as e:
    print "Failed to connect to RPC:"
    print e
