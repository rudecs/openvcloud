from framework.api import  utils

class Sizes:
    def __init__(self, api_client):
        self._api = api_client

    def list(self, ** kwargs):
        return self._api.cloudapi.sizes.list(** kwargs)
