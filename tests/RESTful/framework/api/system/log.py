from framework.api import utils

class Log:
    def __init__(self, api_client):
        self._api = api_client

    def purge(self, age):
        return self._api.system.log.purge(age=age)