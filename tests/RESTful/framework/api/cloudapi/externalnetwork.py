from framework.api import utils

class ExternalNetwork:
    def __init__(self, api_client):
        self._api = api_client

    def list(self, accountId):
        return self._api.cloudapi.externalnetwork.list(accountId=accountId)