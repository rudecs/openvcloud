from framework.api import utils

class GridManager:
    def __init__(self, api_client):
        self._api = api_client

    def getDisks(self, **kwargs):
        return self._api.system.gridmanager.getDisks(**kwargs)

    def getGrids(self):
        return self._api.system.gridmanager.getGrids()

    def getGrids(self):
        return self._api.system.gridmanager.getGrids()

    def getJob(self, id, guid):
        return self._api.system.gridmanager.getJob(id=id, guid=guid)

    def getJobs(self, category, **kwargs):
        return self._api.system.gridmanager.getJobs(category=category, **kwargs)

    def getLogs(self, **kwargs):
        return self._api.system.gridmanager.getLogs(**kwargs)

    def getNodes(self, **kwargs):
        return self._api.system.gridmanager.getNodes(**kwargs)

    def getStatImage(self, statKey, width, height):
        return self._api.system.gridmanager.getStatImage(
            statKey=statKey,
            width=width,
            height=height
        )

    def getVDisks(self, **kwargs):
        return self._api.system.gridmanager.getVDisks(**kwargs)

    

