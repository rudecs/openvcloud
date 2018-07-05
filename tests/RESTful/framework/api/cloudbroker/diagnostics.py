import random
from framework.api import  utils

class Diagnostics:
    def __init__(self, api_client):
        self._api = api_client


    def checkVms(self):
        return self._api.cloudbroker.diagnostics.checkVms()