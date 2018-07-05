from framework.api import utils

class DocGenerator:
    def __init__(self, api_client):
        self._api = api_client

    def prepareCatalog(self):
        return self._api.system.docgenerator.prepareCatalog()