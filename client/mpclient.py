from concurrent.futures import ThreadPoolExecutor
import requests
import json
import base64
import pdb
import sys
from time import time
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


    def parse_token(resp):
        token_resp = resp.json()
        token = token_resp['token']
        exp64 = token+"="*(4-len(token)%4)
        decoded = exp64.decode("base64")
        self.exp =json.loads(decoded)['exp']
        self.token = token_resp


    def login(self):
        resp = requests.post(self.url+'/mp/login',headers={'Content-Type':'application/json; charset=UTF-8'},data= json.dumps({'password':self.password,'username':self.username}))

        if resp.status == 200:
            parse_token(resp)
        else:
            print "END OF THE WORLD!"
            sys.exit(1)

    def refresh(self):
        if long(self.exp)-long(time())<=3000:
            resp = requests.post(self.url+'/mp/refresh',headers={'Content-Type':'application/json; charset=UTF-8'},data= json.dumps({'token':self.token}))
            if resp.status == 400:
                login()
            else:
                parse_token(resp)

    def post_telemetry(self,data):
        refresh()
        resp = requests.post(self.url+'/mp/postTelemetry',data=data)
        return (resp.json()['time'],resp.json()['error'])
        #respond
    def get_server_info(self):
        refresh()
        resp = requests.get(self.url+'/mp/getServerInfo')
        #parse and return

    def get_obstacles(self):
        refresh()
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
