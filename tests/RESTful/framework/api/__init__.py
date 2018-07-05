from testconfig import config
from framework.utils.ovc_client import Client
from framework.utils.utils import Utils

ip = config['main']['ip']
port = int(config['main']['port'])
client_id = config['main']['client_id']
client_secret = config['main']['client_secret']

api_client = Client(ip, port, client_id, client_secret)
api_client.load_swagger()

utils = Utils()