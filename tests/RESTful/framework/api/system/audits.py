from framework.api import utils

class Audits:
    def __init__(self, api_client):
        self._api = api_client

    def listAudits(self, **kwargs):
        return self._api.system.audits.listAudits(** kwargs)
