from framework.api import utils

class ErrorConditionHandler:
    def __init__(self, api_client):
        self._api = api_client

    def delete(self, eco):
        return self._api.system.errorconditionhandler.delete(eco=eco)

    def purge(self, age):
        return self._api.system.errorconditionhandler.purge(age=age)