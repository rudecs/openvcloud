from framework.api import  utils

class Health:
    def __init__(self, api_client):
        self._api = api_client

    def getDetailedStatus(self, nid):
        return self._api.system.health.getDetailedStatus(nid=nid)

    def getOverallStatus(self):
        return self._api.system.health.getOverallStatus()

    def getStatusSummary(self):
        return self._api.system.health.getStatusSummary()

    def refreshCommand(self, nid, cmd):
        return self._api.system.health.refreshCommand(nid=nid, cmd=cmd)

    def run(self, nid):
        return self._api.system.health.run(nid=nid)

