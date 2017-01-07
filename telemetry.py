"""
Interoperbility component that uploads telemetry
"""

from libinterop import TelemetryInterop
import threading

proxy_info ={
	"host": "192.168.123.200",
	"port"  : "8000",
	"username": "telemuser",
	"password": "ruautonomous"

}


poll_info = {
	"poll_sec" : 0.1,
	"print_sec": 10
}

mav_info = {
	"host": "192.168.123.205",
	"port": "14550"
}


telem_client = TelemetryInterop(
	proxy_info,
	poll_info,
	mav_info)
print("STARTING Telemetry Interop Client")
telem_client.start(False)

