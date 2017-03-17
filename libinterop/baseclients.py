from concurrent.futures import ThreadPoolExecutor
import requests
import json
import base64
import binascii
import pdb
import sys
import time
from types import Mission,StationaryObstacle,MovingObstacle
"""
	These classes define the "base" clients used to contact
	the interop proxy server (Imaging GCS django).
"""


STATUS_OK = 200

workers = 5

class _Client(object):
	"""
		synchronous client for the imaging proxy server
	"""

	def __init__(self,url,username,password,timeout=5):
		self.url = url
		self.timeout = timeout
		self.username = username
		self.password = password
		self.login()


	def parse_token(self,resp):
		"""
			the Json-web token returned by the server is base64 encoded
			we need to parse the token and its expiration
			arg := b64 encoded token
		"""
		token_resp = resp.json()
		token = token_resp['token']
		exp64 = token+"="*(4-len(token)%4)
		decoded = exp64.decode("base64")
		self.exp =json.loads(decoded.partition('}')[2].partition('}')[0]+"}")['exp']
		self.token = token_resp


	def login(self):
		global STATUS_OK
		"""
			logs into the Imaging GCS
		"""
		resp = requests.post(self.url+'/interop/login',headers={'Content-Type':'application/json; charset=UTF-8'},data= json.dumps({'password':self.password,'username':self.username}))

		if resp.status_code == STATUS_OK:
			self.parse_token(resp)
		else:
			raise Exception(resp.status_code)

	def post_telemetry(self,data):
		"""
			proxy method for posting telemetry to the interop server
			args := Telemetry object
			returns := tuple(time of response,error)
		"""
		resp =requests.post(self.url+'/interop/postTelemetry',data=data.serialize(), headers={'Authorization':'JWT '+self.token['token']})
		if not resp.ok:
			return (None,"Received %d\n" % resp.status_code)
		if resp.json()['error'] is not None:
			return (None,resp.json()['error'])
		return (resp.json()['time'],resp.json()['error'])

	def get_mission(self):
		"""
			proxy method for fetching missions and returns them as a list in mission object form
			returns := list( Misssion_obj , ... )
		"""
		resp = requests.post(self.url+'/interop/getMission',headers={'Authorization':'JWT '+self.token['token']})
		if not resp.ok:
			return (None,"Received %d\n" % resp.status_code)
		if resp.json()['error'] is not None:
			return (None,resp.json()['error'])
		return ([Mission(**resp.json()[key]) for key in resp.json().keys() if key !='error'],resp.json()['error'])
	def get_obstacles(self):
		"""
			proxy method for fetching moving and stationary obstacles
			returns := tuple( list(moving_obstacle,...), list(stationary_obstacle,..), error )
		"""

		resp = requests.post(self.url+'/interop/getObstacles',headers={'Authorization':'JWT '+self.token['token']})
		if not resp.ok:
			return (None,None,"Received %d\n" % resp.status_code)
		if resp.json()['error'] is not None:
			return (None,None,resp.json()['error'])
		return ([MovingObstacle(**resp.json()['moving'][key]) for key in resp.json()['moving'].keys()],[StationaryObstacle(**resp.json()['stationary'][key]) for key in resp.json()['stationary'].keys()],resp.json()['error'])

class AsyncClient(object):
	"""
		future "enhanced" client for providing pipeling and concurrency
	"""
	def __init__(self,url,username,password):
		"""
			creates the Thread pool executor and logs in 
		"""

		self.executor = ThreadPoolExecutor(max_workers = workers)
		while True:
			try:
				self.client=_Client(url,username,password)
				break
			# due to a weird token formatting error, we need to keep logging in untill a good token is returned
			except(TypeError,binascii.Error):
				continue #continue to attempt upload on token decode failure

	def post_telemetry(self,data):
		return self.executor.submit(self.client.post_telemetry,data)

	def get_mission(self):
		return self.executor.submit(self.client.get_mission)

	def get_obstacles(self):
		return self.executor.submit(self.client.get_obstacles)
