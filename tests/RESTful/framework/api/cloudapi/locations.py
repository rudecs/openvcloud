from framework.api import utils

class Locations:
    def __init__(self, api_client):
        self._api = api_client

    def list(self):
        return self._api.cloudapi.locations.list()

    def getUrl(self):
        return self._api.cloudapi.locations.getUrl()