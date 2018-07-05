from framework.api import utils

class Cloudspaces:
    def __init__(self, api_client):
        self._api = api_client

    def list(self):
        return self._api.cloudapi.cloudspaces.list()

    def get(self, cloudspaceId):
        return self._api.cloudapi.cloudspaces.get(cloudspaceId=cloudspaceId)

    def create(self, accountId, location, access, **kwargs):
        data = {
            'accountId': accountId,
            'location': location,
            'access': access,
            'name': utils.random_string(),
            'maxMemoryCapacity': -1,
            'maxVDiskCapacity': -1,
            'maxCPUCapacity': -1,
            'maxNetworkPeerTransfer': -1,
            'maxNumPublicIP': -1,
            'allowedVMSizes': [],
            'privatenetwork': ''
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.cloudspaces.create(** data)

    def update(self, cloudspaceId, **kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'name': utils.random_string(),
            'maxMemoryCapacity': -1,
            'maxVDiskCapacity': -1,
            'maxCPUCapacity': -1,
            'maxNetworkPeerTransfer': -1,
            'maxNumPublicIP': -1,
            'allowedVMSizes': [],
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.cloudspaces.update(** data)

    def delete(self, cloudspaceId):
        return self._api.cloudapi.cloudspaces.delete(cloudspaceId=cloudspaceId)

    def deploy(self, cloudspaceId):
        return self._api.cloudapi.cloudspaces.deploy(cloudspaceId=cloudspaceId)

    def enable(self, cloudspaceId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudapi.cloudspaces.enable(cloudspaceId=cloudspaceId, reason=reason)

    def disable(self, cloudspaceId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())
        return self._api.cloudapi.cloudspaces.disable(cloudspaceId=cloudspaceId, reason=reason)

    def getDefenseShield(self, cloudspaceId):
        return self._api.cloudapi.cloudspaces.getDefenseShield(cloudspaceId=cloudspaceId)
    
    def getOpenvpnConfig(self, cloudspaceId):
        return self._api.cloudapi.cloudspaces.getOpenvpnConfig(cloudspaceId=cloudspaceId)

    def addAllowedSize(self, cloudspaceId, sizeId):
        return self._api.cloudapi.cloudspaces.addAllowedSize(cloudspaceId=cloudspaceId, sizeId=sizeId)

    def removeAllowedSize(self, cloudspaceId, sizeId):
        return self._api.cloudapi.cloudspaces.removeAllowedSize(cloudspaceId=cloudspaceId, sizeId=sizeId)

    def addUser(self, cloudspaceId, userId, accesstype='ARCXDU'):
        return self._api.cloudapi.cloudspaces.addUser(
            cloudspaceId=cloudspaceId,
            userId=userId,
            accesstype=accesstype
        )

    def deleteUser(self, cloudspaceId, userId, recursivedelete=False):        
        return self._api.cloudapi.cloudspaces.deleteUser(
            cloudspaceId=cloudspaceId,
            userId=userId,
            recursivedelete=recursivedelete
        )

    def updateUser(self, cloudspaceId, userId, accesstype):
        return self._api.cloudapi.cloudspaces.addUser(
            cloudspaceId=cloudspaceId,
            userId=userId,
            accesstype=accesstype
        )

    def executeRouterOSScript(self, cloudspaceId, script):
        return self._api.cloudapi.cloudspaces.executeRouterOSScript(cloudspaceId=cloudspaceId, script=script)

    