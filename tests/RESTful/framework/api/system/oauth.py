from framework.api import utils

class Oauth:
    def __init__(self, api_client):
        self._api = api_client

    def authenticate(self, **kwargs):
        return self._api.system.oauth.authenticate(**kwargs)

    def authorize(self):
        return self._api.system.oauth.authorize()

    def getOauthLogoutURl(self):
        return self._api.system.oauth.getOauthLogoutURl()