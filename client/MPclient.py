from concurrent.futures import ThreadPoolExecutor
import requests

workers = 5
class _Client(object):

    def __init__(self,url,username,password,timeout=5):
        self.url = url
        self.timeout = timeout
        self.username = username
        self.password = password
        self.login()
    def login():
        resp = Request('POST',self.url+'/mp/login',data= {'username':self.username,'password':self.password})
        token = resp.json()

    def post_telemetry(self,data):
        resp = Request('POST',self.url+'/mp/postTelemetry',data=data)
        #respond
    def get_server_info(self):
        resp = Request('GET',self.url+'/mp/getServerInfo')
        #parse and return

    def get_obstacles(self):
        resp = Request('GET',self.url+'/mp/getObstacles')
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
