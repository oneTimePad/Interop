from concurrent.futures import ThreadPoolExecutor
import requests
import json

workers = 5

#TODO:need to add authoriation header
#check how to parse token
#add returning of requests
#returning of exceptions
class _Client(object):

    def __init__(self,url,username,password,timeout=5):
        self.url = url
        self.timeout = timeout
        self.username = username
        self.password = password
        self.login()

    def login(self):
        resp = requests.post(self.url+'/mp/login',headers={'Content-Type':'application/json'},data= json.dumps({'password':self.password,'username':self.username}))
        #token = resp.json()

    def post_telemetry(self,data):
        resp = requests.post(self.url+'/mp/postTelemetry',data=data)
        #respond
    def get_server_info(self):
        resp = requests.get(self.url+'/mp/getServerInfo')
        #parse and return

    def get_obstacles(self):
        resp = requests.get(self.url+'/mp/getObstacles')
        #parse and return

class Client(object):
    def __init__(self,url,username,password):

        self.client=_Client(url,username,password)
        self.executor = ThreadPoolExecutor(max_workers = workers)

    def post_telemetry(self,data):
        return self.executor.submit(self.client.post_telemetry,data)

    def get_server_info(self):
        return self.executor.submit(self.client.get_server_info)

    def get_obstacles(self):
        return self.executor.submit(self.client.get_obstacles)
