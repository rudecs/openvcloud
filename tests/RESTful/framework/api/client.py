from framework.api.cloudapi.cloudapi import Cloudapi
from framework.api.system.system import System
from framework.api.libcloud.libcloud import Libcloud
from framework.api.cloudbroker.cloudbroker import Cloudbroker
from testconfig import config
import time
from framework.utils.ovc_client import Client as api_client
import random



class Client:
    def __init__(self, client_id=None, client_secret=None):

        ip = config['main']['ip']
        port = int(config['main']['port'])
        self.api_client = api_client(ip, port, client_id, client_secret)
        if client_id:
            self.api_client.load_swagger()
        self.cloudapi = Cloudapi(self.api_client)
        self.cloudbroker = Cloudbroker(self.api_client)
        self.libcloud = Libcloud(self.api_client)
        self.system = System(self.api_client)
        self._whoami = config['main']['username']


    def set_auth_header(self, value):
        self.api_client._session.headers['Authorization'] = value

    def create_user(self, **kwargs):
        data, response = self.cloudbroker.user.create(**kwargs)

        if response.status_code != 200:
            return False

        return data['username'], data['password']

    def create_account(self, **kwargs):
        data, response = self.cloudbroker.account.create(username=self._whoami, ** kwargs)

        if response.status_code != 200:
            return False

        account_id = int(response.text)
        return account_id
    
    def create_cloudspace(self, accountId, location, **kwargs):
        data, response = self.cloudapi.cloudspaces.create(accountId=accountId, location=location, access=self._whoami, **kwargs)

        if response.status_code != 200:
            return False

        cloudspace_id = int(response.text)

        for _ in range(20):
            response = self.cloudapi.cloudspaces.get(cloudspaceId=cloudspace_id)
            if response.json()['status'] == 'DEPLOYED':
                break
            time.sleep(5)
        else:
            return False

        return cloudspace_id

    def get_environment(self):
        env_location = config['main']['location']
        locations = (self.api_client.cloudapi.locations.list()).json()
        for location in locations:
            if env_location == location['locationCode']:
                return location
        else:
            raise Exception("can't find the %s environment location in grid" % env_location)

    def get_random_locations(self):
        return random.choice(self.cloudapi.locations.list())['locationCode']

    def wait_for_cloudspace_status(self,cloudspaceId,status= "DEPLOYED", timeout=300):
        response = self.cloudapi.cloudspaces.get(cloudspaceId=cloudspaceId)
        cs_status=response.json()["status"]
        for _ in range(timeout):
            if cs_status == status:
                break
            time.sleep(1)
            response = self.api_client.cloudapi.cloudspaces.get(cloudspaceId=cloudspaceId)
            cs_status=response.json()["status"]

        return cs_status

    def authenticate_user(self, username=None, password=None, **kwargs):
        if not username or password:
            username, password = self.create_user(**kwargs)

        api = Client()
        response = api.system.usermanager.authenticate(name=username, secret=password)
        response.raise_for_status
        return api, username


    def get_running_nodeId(self, except_nodeid=None):
        nodes = self.api_client.cloudbroker.computenode.list().json()
        for node in nodes:
            if int(node['referenceId']) != except_nodeid and node['status'] == 'ENABLED':
                return int(node['referenceId'])
        else:
            return None