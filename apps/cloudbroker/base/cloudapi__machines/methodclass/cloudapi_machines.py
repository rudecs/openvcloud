from JumpScale import j
from cloudapi_machines_osis import cloudapi_machines_osis
from cloudbrokerlib import authenticator
ujson = j.db.serializers.ujson


class cloudapi_machines(cloudapi_machines_osis):

    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """

    def __init__(self):

        self._te = {}
        self.actorname = "machines"
        self.appname = "cloudapi"
        cloudapi_machines_osis.__init__(self)
        self._cb = None

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @authenticator.auth(acl='X')
    def action(self, machineId, actiontype, **kwargs):
        """
        Perform a action on a machine, supported types are STOP, START, PAUSE, RESUME, REBOOT
        param:machineId id of the machine
        param:actiontype type of the action(e.g stop, start, ...)
        result bool

        """
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return self.cb.extensions.imp.machineAction(machine, actiontype)


    @authenticator.auth(acl='C')
    def addDisk(self, machineId, diskName, description, size=10, type='B', **kwargs):
        """
        Add a disk to a machine
        param:machineId id of machine
        param:diskName name of disk
        param:description optional description
        param:size size in GByte default=10
        param:type (B;D;T)  B=Boot;D=Data;T=Temp default=B
        result int

        """
        machine = self.cb.model_vmachine_get(machineId)
        disk = self.cb.models.disk.new()
        disk.name = diskName
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        self.cb.extensions.imp.addDiskToMachine(machine, disk)
        diskid = self.cb.model_disk_set(disk)
        machine['disks'].append(diskid)
        self.cb.model_vmachine_set(machine)
        return diskid

    @authenticator.auth(acl='C')
    def backup(self, machineId, backupName, **kwargs):
        """
        backup is in fact an export of the machine to a cloud system close to the IAAS system on which the machine is running
        param:machineId id of machine to backup
        param:backupName name of backup
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method backup")

    @authenticator.auth(acl='C')
    def create(self, cloudspaceId, name, description, sizeId, imageId, **kwargs):
        """
        Create a machine based on the available flavors, in a certain space.
        The user needs write access rights on the space.
        param:cloudspaceId id of cloudspace in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:size id of the specific size default=1
        param:image id of the specific image
        result bool

        """
        for m in self.list(cloudspaceId, **kwargs):
            if m['name'] == name:
                raise ValueError("Machine with name %s already exists" % name)
        machine = self.cb.models.vmachine.new()
        machine.cloudspaceId = cloudspaceId
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId
        machine.id = self.cb.model_vmachine_set(machine.obj2dict())
        self.cb.extensions.imp.createMachine(machine)
        return self.cb.model_vmachine_set(machine.obj2dict())

    @authenticator.auth(acl='D')
    def delDisk(self, machineId, diskId, **kwargs):
        """
        Delete a disk from machine
        param:machineId id of machine
        param:diskId id of disk to delete
        result bool

        """
        machine = self.cb.model_vmachine_get(machineId)
        diskfound = diskId in machine['disks']
        if diskfound:
            machine['disks'].remove(diskId)
            self.cb.model_vmachine_set(machine)
            self.cb.model_disk_delete(diskId)
        return diskfound

    @authenticator.auth(acl='D')
    def delete(self, machineId, **kwargs):
        """
        Delete a machine
        param:machineId id of the machine
        result

        """
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        self.cb.extensions.imp.deleteMachine(machine)
        return self.cb.model_vmachine_delete(machineId)

    def exporttoremote(self, machineId, exportName, uncpath, **kwargs):
        """
        param:machineId id of machine to export
        param:exportName give name to export action
        param:uncpath unique path where to export machine to ()
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method exporttoremote")

    @authenticator.auth(acl='R')
    def get(self, machineId, **kwargs):
        """
        Get information from a certain object.
        This contains all information about the machine.
        param:machineId id of machine
        result

        """
        machine = self.cb.model_vmachine_get(machineId)
        print machine
        return {'id': machine['id'], 'cloudspaceid': machine['cloudspaceId'], 
        'name': machine['name'], 'hostname':machine['hostName'],
         'status':machine['status'], 'imageid':machine['imageId'], 'sizeid':machine['sizeId'],
         'interfaces':machine['nics']}   

    def importtoremote(self, name, uncpath, **kwargs):
        """
        param:name name of machine
        param:uncpath unique path where to import machine from ()
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method importtoremote")

    @authenticator.auth(acl='R')
    def list(self, cloudspaceId, type=None, **kwargs):
        """
        List the deployed machines in a space. Filtering based on status is possible.
        param:cloudspaceId id of cloudspace in which machine exists
        param:type when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT)
        result list

        """
        term = dict()
        if cloudspaceId:
            term["cloudspaceId"] = cloudspaceId
        if type: 
            term["type"] = type
        if not term:
            return self.cb.model_vmachine_list()
        query = {'query': {'term': term }, 'fields': ['id', 'cloudspaceid','hostname', 'imageId', 'name', 'nics', 'sizeId', 'status']}
        results = self.cb.model_vmachine_find(ujson.dumps(query))['result']
        machines = [res['fields'] for res in results]
        return machines

    @authenticator.auth(acl='C')
    def snapshot(self, machineId, snapshotname, **kwargs):
        """
        param:machineId id of machine to snapshot
        param:snapshotname Optional name to give snapshot
        result int

        """
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return self.cb.extensions.imp.snapshot(machine, snapshotname)


    @authenticator.auth(acl='C')
    def listSnapshots(self, machineId, **kwargs):
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return self.cb.extensions.imp.listSnapshots(machine)

    @authenticator.auth(acl='C')
    def deleteSnapshot(self, machineId, name, **kwargs):
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return self.cb.extensions.imp.deleteSnapshot(machine, name)

    @authenticator.auth(acl='C')
    def rollbackSnapshot(self, machineId, name, **kwargs):
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return self.cb.extensions.imp.rollbackSnapshot(machine, name)

    def update(self, machineId, name, description, size, **kwargs):
        """
        Change basic properties of a machine.
        Name, description can be changed with this action.
        param:machineId id of the machine
        param:name name of the machine
        param:description description of the machine
        param:size size of the machine in CU

        """
        machine = self.get(machineId)
        if name is not None:
            machine['name'] = name
        if description is not None:
            machine['description'] = description
        if size is not None:
            machine['nrCU'] = size
        return self.cb.model_vmachine_set(machine)
