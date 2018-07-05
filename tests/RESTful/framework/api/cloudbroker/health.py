import random
from framework.api import utils

class Health:
    def __init__(self, api_client):
        self._api = api_client


    def status(self):
        return self._api.cloudbroker.health.status()