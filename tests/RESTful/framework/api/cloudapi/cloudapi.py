from framework.api.cloudapi.accounts import Accounts
from framework.api.cloudapi.cloudspaces import Cloudspaces
from framework.api.cloudapi.disks import Disks
from framework.api.cloudapi.externalnetwork import ExternalNetwork
from framework.api.cloudapi.images import Images
from framework.api.cloudapi.locations import Locations
from framework.api.cloudapi.machines import Machines
from framework.api.cloudapi.portforwarding import Portforwarding
from framework.api.cloudapi.sizes import Sizes
from framework.api.cloudapi.users import Users

class Cloudapi:
    def __init__(self, api_client):
        self.accounts = Accounts(api_client)
        self.cloudspaces = Cloudspaces(api_client)
        self.disks = Disks(api_client)
        self.externalnetwork = ExternalNetwork(api_client)
        self.images = Images(api_client)
        self.locations = Locations(api_client)
        self.machines = Machines(api_client)
        self.portforwarding = Portforwarding(api_client)
        self.sizes = Sizes(api_client)
        self.users = Users(api_client)
