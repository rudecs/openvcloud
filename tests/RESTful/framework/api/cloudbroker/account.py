import random
from framework.api import utils

class Account:
    def __init__(self, api_client):
        self._api = api_client

    def addUser(self, username, accountId, **kwargs):
        data = {
            'username': username,
            'accountId': accountId,
            'accesstype': random.choice(['R','RCX','ARCX'])
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.account.addUser(** data)

    def create(self, username, **kwargs):
        data = {
            "name" : utils.random_string(),
            "username" : username,
            "maxMemoryCapacity": -1,
            "maxVDiskCapacity": -1,
            "maxCPUCapacity": -1,
            "maxNetworkPeerTransfer": -1,
            "maxNumPublicIP": -1
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.account.create(**data)

    def delete(self, accountId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudbroker.account.delete(accountId=accountId,reason=reason)
    
    def deleteAccounts(self, accountIds, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudbroker.account.deleteAccounts(accountIds=accountIds, reason=reason)

    def update(self, accountId, **kwargs):
        data = {
            'accountId': accountId,
            'name': utils.random_string(),
            'maxMemoryCapacity': -1,
            'maxVDiskCapacity': -1,
            'maxCPUCapacity': -1,
            'maxNetworkPeerTransfer': -1,
            'maxNumPublicIP': -1
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.account.update(** data)

    def deleteUser(self, accountId, userId, recursivedelete=False):        
        return self._api.cloudbroker.account.deleteUser(
            accountId=accountId,
            userId=userId,
            recursivedelete=recursivedelete
        )

    def updateUser(self, accountId, userId, accesstype):
        return self._api.cloudbroker.account.addUser(
            accountId=accountId,
            userId=userId,
            accesstype=accesstype
        )

    def disable(self, accountId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudbroker.account.disable(accountId=accountId, reason=reason)

    def enable(self, accountId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudbroker.account.enable(accountId=accountId, reason=reason)
