from framework.api import utils
from framework.api.cloudbroker.account import Account
from framework.api.cloudbroker.cloudspace import Cloudspace
from framework.api.cloudbroker.diagnostics import Diagnostics
from framework.api.cloudbroker.health import Health
from framework.api.cloudbroker.iaas import Iaas
from framework.api.cloudbroker.image import Image
from framework.api.cloudbroker.machine import Machine
from framework.api.cloudbroker.ovsnode import OVSNode
from framework.api.cloudbroker.qos import Qos
from framework.api.cloudbroker.user import User

class Cloudbroker:

    def __init__(self, api_client):
        self.account = Account(api_client)
        self.cloudspace = Cloudspace(api_client)
        self.diagnostics = Diagnostics(api_client)
        self.health = Health(api_client)
        self.iaas = Iaas(api_client)
        self.image = Image(api_client)
        self.machine = Machine(api_client)
        self.ovsnode = OVSNode(api_client)
        self.qos = Qos(api_client)
        self.user = User(api_client)
