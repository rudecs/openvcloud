from framework.api.libcloud.libvirt import Libvirt

class Libcloud:
    def __init__(self, api_client):
        self.libvirt = Libvirt(api_client)