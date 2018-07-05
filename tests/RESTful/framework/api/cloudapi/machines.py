from framework.api import utils
import random 

class Machines:
    def __init__(self, api_client):
        self._api = api_client

    def addDisk(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'diskName': utils.random_string(),
            'description': utils.random_string(),
            'size': random.randint(1, 1000),
            'ssdSize': random.randint(1, 1000),
            'type': random.choice(['D', 'B', 'T']),
            'iops': random.randint(100, 5000)
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.machines.addDisk(** data)

    def addUser(self, machineId, userId, accesstype='ARCXDU'):        
        return self._api.cloudapi.machines.addUser(machineId=machineId,
            userId=userId,
            accesstype=accesstype
        )

    def attachDisk(self, machineId, diskId):        
        return self._api.cloudapi.machines.attachDisk(machineId=machineId,diskId=diskId)
    
    def attachExternalNetwork(self, machineId):        
        return self._api.cloudapi.machines.attachExternalNetwork(machineId=machineId)

    def clone(self, machineId, **kwargs):   
        name = kwargs.get('name', utils.random_string())     
        return self._api.cloudapi.machines.clone(machineId=machineId, name=name, **kwargs)

    def convertToTemplate(self, machineId, **kwargs):   
        templatename = kwargs.get('templatename', utils.random_string())     
        return self._api.cloudapi.machines.convertToTemplate(machineId=machineId, templatename=templatename)

    def create(self, cloudspaceId, **kwargs):
        data = {
            'cloudspaceId': cloudspaceId,
            'name': utils.random_string(),
            'description': utils.random_string(),
            'datadisks': [],
            'userdata': ''
        }
        response = self._api.cloudapi.images.list()
        response.raise_for_status()
        image = random.choice([x for x in response.json() if x["type"].startswith(('Window', 'Linux'))])
        data['imageId'] = image['id']
        response.raise_for_status()

        response = self._api.cloudapi.sizes.list(cloudspaceId=cloudspaceId)
        response.raise_for_status()
        sizes =response.json()

        basic_sizes=[512, 1024, 4096, 8192, 16384, 2048]
        for _ in range(len(sizes)) :
            size = random.choice(sizes)
            if size["memory"] in basic_sizes:
                break
                
        data['disksize']= random.choice(size['disks'])
        data['sizeId']=size['id']
  
        data.update(** kwargs)
        return data,self._api.cloudbroker.machine.create(**data)

    def delete(self, machineId):   
        return self._api.cloudapi.machines.delete(machineId=machineId)

    def deleteSnapshot(self, machineId, **kwargs):
        return self._api.cloudapi.machines.deleteSnapshot(machineId=machineId, **kwargs)

    def deleteUser(self, machineId, userId):
        return self._api.cloudapi.machines.deleteUser(machineId=machineId, userId=userId)

    def detachDisk(self, machineId, diskId):
        return self._api.cloudapi.machines.deletedetachDiskUser(machineId=machineId, userId=userId)

    def detachExternalNetwork(self, machineId):
        return self._api.cloudapi.machines.detachExternalNetwork(machineId=machineId)

    def exportOVF(self, link, username, passwd, path, machineId, **kwargs):
        return self._api.cloudapi.machines.exportOVF(
            link=link,
            username=username,
            passwd=passwd,
            path=path,
            machineId=machineId,
            **kwargs
        )

    def importOVF(self, link, username, passwd, path, cloudspaceId, sizeId, **kwargs):
        name = kwargs.get('name', utils.random_string())    
        description = kwargs.get('description', utils.random_string()) 

        return self._api.cloudapi.machines.importOVF(
            link=link,
            username=username,
            passwd=passwd,
            path=path,
            cloudspaceId=cloudspaceId,
            name=name,
            description=description,
            sizeId=sizeId,
            **kwargs
        )

    def get(self, machineId):   
        return self._api.cloudapi.machines.get(machineId=machineId)

    def getConsoleUrl(self, machineId):   
        return self._api.cloudapi.machines.getConsoleUrl(machineId=machineId)

    def getHistory(self, machineId):   
        return self._api.cloudapi.machines.getHistory(machineId=machineId)

    def list(self, cloudspaceId):   
        return self._api.cloudapi.machines.list(cloudspaceId=cloudspaceId)

    def listSnapshots(self, machineId):   
        return self._api.cloudapi.machines.listSnapshots(machineId=machineId)

    def pause(self, machineId):   
        return self._api.cloudapi.machines.pause(machineId=machineId)
    
    def reboot(self, machineId):   
        return self._api.cloudapi.machines.reboot(machineId=machineId)

    def reset(self, machineId):   
        return self._api.cloudapi.machines.reset(machineId=machineId)

    def resume(self, machineId):   
        return self._api.cloudapi.machines.resume(machineId=machineId)

    def start(self, machineId):   
        return self._api.cloudapi.machines.start(machineId=machineId)

    def stop(self, machineId):   
        return self._api.cloudapi.machines.stop(machineId=machineId)

    def resize(self, machineId, sizeId):   
        return self._api.cloudapi.machines.resize(machineId=machineId, sizeId=sizeId)

    def rollbackSnapshot(self, machineId, **kwargs):
        return self._api.cloudapi.machines.rollbackSnapshot(machineId=machineId, **kwargs)

    def snapshot(self, machineId):
        data = {
            'machineId':machineId,
            'name': utils.random_string()
        }
        data.update(** kwargs)
        return self._api.cloudapi.machines.snapshot(** data)

    def update(self, machineId, **kwargs):
        data = {
            'machineId': machineId,
            'name': utils.random_string(),
            'description': utils.random_string(),
        }
        data.update(** kwargs)
        return data, self._api.cloudapi.machines.update(** data)

    def updateUser(self, machineId, userId, accesstype):
        return self._api.cloudapi.machines.updateUser(
            machineId=machineId, 
            userId=userId,
            accesstype=accesstype
        )