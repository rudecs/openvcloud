from framework.api import utils

class Job:
    def __init__(self,api_client):
        self._api = api_client

    def purge(self, age):
        return self._api.system.job.purge(age=age)