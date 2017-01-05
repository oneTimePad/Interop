from concurrent.futures import ThreadPoolExecutor
import requests
import json
import base64
import pdb
import sys
import time
from types import Mission,StationaryObstacle,MovingObstacle
workers = 5

class _Client(object):
    def __init__(self,url,username,password,timeout=5):
        self.url = url
        self.timeout = timeout
        self.username = username
        self.password = password
        self.login()


    def parse_token(self,resp):
        token_resp = resp.json()
        token = token_resp['token']
        exp64 = token+"="*(4-len(token)%4)
        decoded = exp64.decode("base64")
        self.exp =json.loads(decoded.partition('}')[2].partition('}')[0]+"}")['exp']
        self.token = token_resp


    def login(self):
        resp = requests.post(self.url+'/interop/login',headers={'Content-Type':'application/json; charset=UTF-8'},data= json.dumps({'password':self.password,'username':self.username}))

        if resp.status_code == 200:
            self.parse_token(resp)
        else:
            raise Exception(resp.status_code)

    def refresh(self):
        if long(self.exp)-long(time.time())<=3000:
            resp = requests.post(self.url+'/interop/refresh',headers={'Content-Type':'application/json; charset=UTF-8'},data= json.dumps({'token':self.token}))
            if resp.status_code == 400:
                self.login()
            else:
                self.parse_token(resp)

    def post_telemetry(self,data):
        #self.refresh()
        resp =requests.post(self.url+'/interop/postTelemetry',data=data.serialize(), headers={'Authorization':'JWT '+self.token['token']})
        return (resp.json()['time'],resp.json()['error'])
        #respond

    def get_mission(self):
        """
        fetches missions and returns them as a list in mission object form
        """
        resp = requests.post(self.url+'/interop/getMission',headers={'Authorization':'JWT '+self.token['token']})
        return ([Mission(**resp.json()[key]) for key in resp.json().keys() if key !='error'],resp.json()['error'])
    def get_obstacles(self):
        """
        fetches moving and stationary obstacles and returns as
        (list(moving obstacles), list(stationry obstacles), error)
        obstacles are in object format
        """

        resp = requests.post(self.url+'/interop/getObstacles',headers={'Authorization':'JWT '+self.token['token']})

        return ([MovingObstacle(**resp.json()['moving'][key]) for key in resp.json()['moving'].keys()],[StationaryObstacle(**resp.json()['stationary'][key]) for key in resp.json()['stationary'].keys()],resp.json()['error'])

class InteropClient(object):
    def __init__(self,url,username,password):

        self.client=_Client(url,username,password)
        self.executor = ThreadPoolExecutor(max_workers = workers)

    def post_telemetry(self,data):
        return self.executor.submit(self.client.post_telemetry,data)

    def get_mission(self):
        return self.executor.submit(self.client.get_mission)

    def get_obstacles(self):
        return self.executor.submit(self.client.get_obstacles)
