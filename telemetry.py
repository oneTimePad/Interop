"""
Interoperbility component that uploads telemetry
"""

from libinterop import TelemetryInterop
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("server",help="ip:port pair for django")
parser.add_argument("username",help="username for django")
parser.add_argument("password", help="password for django")
parser.add_argument("mavproxy",help="ip:port pair for mav")
args = parser.parse_args()
proxy_info ={
	"host": args.server.split(':')[0],
	"port"  : args.server.split(':')[1],
	"username":args.username,
	"password": args.password

}


poll_info = {
	"poll_sec" : 0.1,
	"print_sec": 10
}

mav_info = {
	"host": args.mavproxy.split(':')[0],
	"port": args.mavproxy.split(':')[1]
}


telem_client = TelemetryInterop(
	proxy_info,
	poll_info,
	mav_info)
print("STARTING Telemetry Interop Client")
telem_client.start(False)
