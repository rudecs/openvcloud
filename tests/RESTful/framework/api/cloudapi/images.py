from framework.api import utils

class Images:
    def __init__(self, api_client):
        self._api = api_client

    def list(self, **kwargs):
        return self._api.cloudapi.images.list(**kwargs)

    def delete(self, imageId):
        return self._api.cloudapi.images.delete(imageId=imageId)