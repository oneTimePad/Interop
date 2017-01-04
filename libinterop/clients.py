from libinterop import InteropClient
from libinterop import Telemetry
import binascii
import time


class HandlerInteropClient(InteropClient):

	def __init__(self,proxy_info,poll_info,callback=None,status_debug = True):
		if not all(key in proxy_info for key in("username","password","host","port")):
			raise Exception("HandlerInteropClient<Bad argument>: prox_info = \
				   dict('username','password','host','port')")
		self.future_callback = callback
		self.status_debug = status_debug
		if status_debug:
			import datetime
			self.status_lock = threading.Lock()
			self.sent_since_print = 0
			self.last_print = datetime.datate.now()
		self.POLL_SEC = poll_info["poll_sec"]
		self.PRINT_SEC = poll_info["print_sec"] if ("print_sec" in poll_info)else 0


		while True:
			try:
				super(HandlerInteropClient,self).__init__("http://"+proxy_info["host"]+":"+proxy_info["port"],proxy_info["username"],proxy_info["password"])
				break
			except(TypeError,binascii.Error):
				continue #continue to attempt upload on token decode failure

	def handler_contact_callback(self,future):

		if future.exception():
			print("WARNING: Request Failed with %s" % (str(future.exception())))
		else:
			if self.status_debug:
				print("DEBUG: Request result %s" %(future.result()))
				with self.status_lock:
					sent_sine_print+=1
			if self.future_callback:
				try:
					self.future_callback(*future.result())
				except Exception as e:
					print("WARNING: Registered callback Failed with %s" % (str(e)))
		
	def _make_request(self):
		raise NotImplementedError("_make_request must be overridden")
	
	def start(self,THREADING_ENABLED=True):
		if not THREADING_ENABLED:
			self._start()
		else:
			self.thread = threading.Thread(target=self_start)
			self.thread.start()


	def _start(self):
		try:
			self._make_request()
		except Exception as e:
			raise Exception("WARNING: Request for Object Failed with %s" %
 (str(e)))
		if not self.status_debug:
			pass
		else:
			now = datetime.datetime.now()
			since_print = (now-last_print).total_seconds()

			if since_print >= self.PRINT_SEC:
				with self.status_lock:
					local_sent_since_print = self.sent_since_print
					self.sent_since_print = 0
					print("DEBUG: Upload Rate %f"
  %(local_sent_since_print/since_print))
					self.last_print = now
		time.sleep(self.POLL_SEC)




class TelemetryInterop(HandlerInteropClient):
	def __init__(self,proxy_info,poll_info,mav_info,status_debug=True):
		if not all(key in mav_info for key in ("host","port")):
			raise Exception("TelemtryInterop required mav_info=dict('host','port') to contact mavproxy")
		self.mav_endpoint = mav_info["host"] +":"+mav_info["port"]
		
		try:
			self.drone = dronekit.connect(self.mav_endpoint,wait_ready=True)
		except Exception as e:
			print("TelemetryInterop failed to setup mav connection, Failed with\
		 %s" %(str(e)))
		
		self.last_telemtry = Telemetry(0,0,0,0)

		super(TelemetryInterop,self).__init__(proxy_info,poll_info,status_debug)

	def _make_request(self):
		drone = self.drone
		#TODO : make data accurate
		telemtry = Telemetry(latitude=float(drone.location.global_frame.lat),
					   longitude=float(drone.location.global_frame.lon),
					   altitude_msl=float(drone.location.global_frame.alt),
					   uas_heading = 0)
		if telemtry != self.last_telemtry:
			self.post_telemetry(telemetry).add_done_callback(self.handler_contact_callback)


class ObstacleInterop(HandlerInteropClient):
	
	def _make_request(self):
		self.get_obstacles()

class MissionInterop(InteropClient):
	def __init__(self,proxy_info):
		super(MissionInterop,self).__init__("http://"+proxy_info["host"]+":"+proxy_info["port"],
									  proxy_info["username"],
									  proxy_info["password"])

	def start(self):
		return self.get_mission().result()


