from framework.api import utils
import random

class Accounts:
    def __init__(self, api_client):
        self._api = api_client

    def list(self):
        return self._api.cloudapi.accounts.list()
    
    def get(self, accountId):
        return self._api.cloudapi.accounts.get(accountId=accountId)

    def create(self, access, **kwargs):
        data = {
            'name': utils.random_string(),
            'access': access,
            'maxMemoryCapacity': -1,
            'maxVDiskCapacity': -1,
            'maxCPUCapacity': -1,
            'maxNetworkPeerTransfer': -1,
            'maxNumPublicIP': -1,
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.accounts.create(** data)

    def update(self, accountId, **kwargs):
        return self._api.cloudapi.accounts.update(accountId=accountId, **kwargs)
    
    def addUser(self, accountId, userId, accesstype='ARCXDU'):
        return self._api.cloudapi.accounts.addUser(
            accountId=accountId,
            userId=userId,
            accesstype=accesstype
        )

    def deleteUser(self, accountId, userId, recursivedelete=False):        
        return self._api.cloudapi.accounts.deleteUser(
            accountId=accountId,
            userId=userId,
            recursivedelete=recursivedelete
        )

    def updateUser(self, accountId, userId, **kwargs):
        data = {
            'accountId': accountId,
            'userId': userId,
            'accesstype':random.choice(['R', 'RCX', 'ARCXDU'])
        }
        data.update(**kwargs)
        return data, self._api.cloudapi.accounts.updateUser(** data)

    def listTemplates(self, accountId):
        return self._api.cloudapi.accounts.listTemplates(accountId=accountId)

    def getConsumedCloudUnits(self, accountId):
        return self._api.cloudapi.accounts.getConsumedCloudUnits(accountId=accountId)
    
    def getConsumedCloudUnitsByType(self, accountId, **kwargs):
        data = {
            'accountId':accountId,
            'cutype': random.choice(['CU_M', 'CU_C', 'CU_D', 'CU_S', 'CU_A', 'CU_NO', 'CU_NP', 'CU_I'])
        }
        data.update(**kwargs)
        return self._api.cloudapi.accounts.getConsumedCloudUnitsByType(** data)

    def getConsumption(self, accountId, start, end):
        return self._api.cloudapi.accounts.getConsumption(
            accountId=accountId,
            start=start,
            end=end
        )
    
