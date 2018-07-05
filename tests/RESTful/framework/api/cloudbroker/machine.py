import random
from framework.api import utils


class Machine:
    def __init__(self, api_client):
        self._api = api_client

    def addDisk(self, machineId	,**kwargs):
        pass
        
    def addUser(self, username, machineId, **kwargs):
        data = {
            'username': username,
            'machineId': machineId,
            'accesstype': random.choice(['R','RCX','ARCX'])
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.machine.addUser(** data)
    
    def attachExternalNetwork(self, machineId):
        return self._api.cloudbroker.machine.attachExternalNetwork(machineId=machineId)

    def clone(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'cloneName': utils.random_string(),
            'reason': utils.random_string
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.machine.clone(**data)        

    def convertToTemplate(self, machineId, **kwargs):
        data = {
            'machineId':machineId,
            'templateName':utils.random_string(),
            'reason':utils.random_string()
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.machine.convertToTemplate(** data)     

    def create(self, cloudspaceId, **kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'name': utils.random_string(),
            'description': utils.random_string(),
            'datadisks': [],
            'userdata': ''
        }
        response = self._api.cloudbroker.machine.cloudapi.images.list()
        response.raise_for_status()
        image = random.choice([x for x in response.json() if x.startswith(('Window', 'Linux'))])
        data['imageId'] = image['id']

        sizes = api_client.cloudapi.sizes.list(cloudspaceId=cloudspaceId)
        basic_sizes=[512, 1024, 4096, 8192, 16384, 2048]
        size = [ size for size in sizes if size['memory'] in basic_sizes][0]
        data['disksize']= random.choice(size['disks'])
        data['sizeId']=size['id']
  
        data.update(** kwargs)
        return data,self._api.cloudbroker.machine.create(**data)

    def createPortForward(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'localport': random.randint(1000, 5000),
            'destPort': random.randint(1000, 5000),
            'protocol': random.choice(['udp', 'tcp'])
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.machine.createPortForward(** data)

    def deletePortForward(self, machineId, localport, destPort, protocol):
        return self._api.cloudbroker.machine.deletePortForward(
            machineId=machineId,
            localport=localport,
            destPort=destPort,
            protocol=protocol
        )
        
    def deleteDisk(self, machineId, diskId):
        return self._api.cloudbroker.machine.deleteDisk(machineId=machineId, diskId=diskId)
    
    def deleteUser(self, machineId, userId):        
        return self._api.cloudbroker.machine.deleteUser(
            machineId=machineId,
            userId=userId
        )

    def deleteSnapshot(self, machineId, epoch, reason):
        return self._api.cloudbroker.machine.deleteSnapshot(machineId=machineId, epoch=epoch, reason=reason)

    def destroy(self, machineId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.destroy(machineId=machineId, reason=reason)

    def destroyMachines(self, machineIds,**kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.destroyMachines(machineIds=machineIds, reason=reason)

    def detachExternalNetwork(self, machineId):
        return self._api.cloudbroker.machine.detachExternalNetwork(machineId=machineId)

    def get(self, machineId):
        return self._api.cloudbroker.machine.get(machineId=machineId)
        
    def getHistory(self, machineId):
        return self._api.cloudbroker.machine.getHistory(machineId=machineId)

    def listPortForwards(self, machineId, **kwargs):
        result = kwargs.get('result', utils.random_string())       
        return self._api.cloudbroker.machine.listPortForwards(machineId=machineId, result=result)

    def listSnapshots(self, machineId):
        return self._api.cloudbroker.machine.listSnapshots(machineId=machineId)

    def pause(self, machineId, **kwargs):
        reason = kwargs.get('reason',utils.random_string())       
        return self._api.cloudbroker.machine.pause(machineId=machineId, reason=reason)

    def reboot(self, machineId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.reboot(machineId=machineId, reason=reason)

    def rebootMachines(self, machineIds, **kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.rebootMachines(machineIds=machineIds, reason=reason)

    def restore(self, machineId, **kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.restore(machineId=machineId, reason=reason)

    def resume(self, machineId,**kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.resume(machineId=machineId, reason=reason)

    def start(self, machineId,**kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.start(machineId=machineId, reason=reason)

    def startMachines(self, machineIds,**kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.startMachines(machineIds=machineIds, reason=reason)

    def stop(self, machineId,**kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.stop(machineId=machineId, reason=reason)

    def stopMachines(self, machineIds, **kwargs):
        reason = kwargs.get('reason', utils.random_string())       
        return self._api.cloudbroker.machine.stopMachines(machineIds=machineIds, reason=reason)

    def moveToDifferentComputeNode(self, machineId,**kwargs):
        pass

    def rollbackSnapshot(self, machineId, **kwargs):
        return self._api.cloudbroker.machine.rollbackSnapshot(machineId=machineId, **kwargs)

    def snapshot(self, machineId, **kwargs):
        data = {
            "machineId":machineId,
            "snapshotname":utils.random_string(),
            "reason":utils.random_string
        }
        data.update(**kwargs)
        return data, self._api.cloudbroker.machine.snapshot(**data)

    def tag(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'tag': utils.random_string()
        }
        data.update(** kwargs)    
        return data, self._api.cloudbroker.machine.tag(machineId=machineId, tagName=tagName)        

    def untag(self, machineId, tagName):
        return self._api.cloudbroker.machine.untag(machineId=machineId, tagName=tagName)

    def update(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'name': utils.random_string(),
            'description': utils.random_string(),
        }
        data.update(** kwargs)
        return data, self._api.cloudbroker.machine.update(** data)

        
