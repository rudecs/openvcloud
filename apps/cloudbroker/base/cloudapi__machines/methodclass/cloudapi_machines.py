from JumpScale import j
from cloudapi_machines_osis import cloudapi_machines_osis
from cloudbrokerlib import authenticator, enums
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

    def _action(self, machineId, actiontype, newstatus=None, **kwargs):
        """
        Perform a action on a machine, supported types are STOP, START, PAUSE, RESUME, REBOOT
        param:machineId id of the machine
        param:actiontype type of the action(e.g stop, start, ...)
        result bool

        """
        machine = self._getMachine(machineId)
        node = self._getNode(machine.referenceId)
        provider = self._getProvider(machine)
        actionname = "%s_node" % actiontype.lower()
        method = getattr(provider.client, actionname, None)
        if not method:
            method = getattr(provider.client, "ex_%s" % actiontype.lower(), None)
            if not method:
                raise RuntimeError("Action %s is not support on machine %s" % (actiontype, machineId))
        if newstatus and newstatus != machine.status:
            machine.status = newstatus
            self.cb.model_vmachine_set(machine)
        return method(node)

    @authenticator.auth(acl='X')
    def start(self, machineId, **kwargs):
        return self._action(machineId, 'start', enums.MachineStatus.RUNNING)

    @authenticator.auth(acl='X')
    def stop(self, machineId, **kwargs):
        return self._action(machineId, 'stop', enums.MachineStatus.HALTED)

    @authenticator.auth(acl='X')
    def reboot(self, machineId, **kwargs):
        return self._action(machineId, 'reboot', enums.MachineStatus.RUNNING)

    @authenticator.auth(acl='X')
    def pause(self, machineId, **kwargs):
        return self._action(machineId, 'suspend', enums.MachineStatus.SUSPENDED)

    @authenticator.auth(acl='X')
    def resume(self, machineId, **kwargs):
        return self._action(machineId, 'resume', enums.MachineStatus.RUNNING)

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

    def _getProvider(self, machine):
        if machine.referenceId and machine.stackId:
            return self.cb.extensions.imp.getProviderByStackId(machine.stackId)
        return None

    @authenticator.auth(acl='C')
    def create(self, cloudspaceId, name, description, sizeId, imageId, disksize, **kwargs):
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
        if not disksize:
            raise ValueError("Invalid disksize %s" % disksize)

        machine = self.cb.models.vmachine.new()
        machine.cloudspaceId = cloudspaceId
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId

        disk = self.cb.models.disk.new()
        disk.name = '%s_1'
        disk.descr = 'Machine boot disk'
        disk.sizeMax = disksize
        diskid = self.cb.model_disk_set(disk)
        machine.disks.append(diskid)
        machine.id = self.cb.model_vmachine_set(machine)
        try:
            stack = self.cb.extensions.imp.getBestProvider(imageId)
            provider = self.cb.extensions.imp.getProviderByStackId(stack['id'])
            brokersize = self.cb.model_size_get(machine.sizeId)
            firstdisk = self.cb.model_disk_get(machine.disks[0])
            psize = provider.getSize(brokersize, firstdisk)
            image, pimage = provider.getImage(machine.imageId)
            machine.cpus = psize.vcpus if hasattr(psize, 'vcpus') else None
            name = 'vm-%s' % machine.id
        except:
            self.cb.model_vmachine_delete(machine.id)
            raise
        node = provider.client.create_node(name=name, image=pimage, size=psize)
        machine.referenceId = node.id
        machine.referenceSizeId = psize.id
        machine.stackId = stack['id']
        machine.status = enums.MachineStatus.RUNNING
        machine.hostName = node.name
        for ipaddress in node.public_ips:
            nic = machine.new_nic()
            nic.ipAddress = ipaddress
        self.cb.model_vmachine_set(machine.obj2dict())

        cloudspace = self.cb.model_cloudspace_new()
        cloudspace.dict2obj(self.cb.model_cloudspace_get(cloudspaceId))
        cloudspace.resourceProviderStacks.append(stack['id'])
        self.cb.model_cloudspace_set(cloudspace)

        return machine.id

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
        provider, node = self._getProviderAndNode(machineId)
        if provider:
            for pnode in provider.client.list_nodes():
                if node.id == pnode.id:
                    provider.client.destroy_node(pnode)
                    break
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
        return {'id': machine['id'], 'cloudspaceid': machine['cloudspaceId'],
                'name': machine['name'], 'hostname': machine['hostName'],
                'status': machine['status'], 'imageid': machine['imageId'], 'sizeid': machine['sizeId'],
                'interfaces': machine['nics']}

    def importtoremote(self, name, uncpath, **kwargs):
        """
        param:name name of machine
        param:uncpath unique path where to import machine from ()
        result int

        """
        # put your code here to implement this method
        raise NotImplementedError("not implemented method importtoremote")

    @authenticator.auth(acl='R')
    def list(self, cloudspaceId, status=None, **kwargs):
        """
        List the deployed machines in a space. Filtering based on status is possible.
        param:cloudspaceId id of cloudspace in which machine exists
        param:status when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT)
        result list

        """
        term = dict()
        if cloudspaceId:
            term["cloudspaceId"] = cloudspaceId
        if status:
            term["status"] = status
        query = {'fields': ['id', 'referenceId', 'cloudspaceid', 'hostname', 'imageId', 'name', 'nics', 'sizeId', 'status']}
        if term:
            query['query'] = {'term': term}
        results = self.cb.model_vmachine_find(ujson.dumps(query))['result']
        machines = [res['fields'] for res in results]
        return machines

    def _getMachine(self, machineId):
        machine = self.cb.model_vmachine_new()
        machine.dict2obj(self.cb.model_vmachine_get(machineId))
        return machine

    def _getNode(self, referenceId):
        return self.cb.extensions.imp.Dummy(id=referenceId)

    def _getProviderAndNode(self, machineId):
        machine = self._getMachine(machineId)
        provider = self._getProvider(machine)
        return provider, self.cb.extensions.imp.Dummy(id=machine.referenceId)

    @authenticator.auth(acl='C')
    def snapshot(self, machineId, snapshotname, **kwargs):
        """
        param:machineId id of machine to snapshot
        param:snapshotname Optional name to give snapshot
        result int

        """
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_snapshot(node, snapshotname)

    @authenticator.auth(acl='C')
    def listSnapshots(self, machineId, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_listsnapshots(node)

    @authenticator.auth(acl='C')
    def deleteSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_snapshot_delete(node, name)

    @authenticator.auth(acl='C')
    def rollbackSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_snapshot_rollback(node, name)

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

    def getConsoleUrl(self, machineId, **kwargs):
        """
        get url to connect to console
        param:machineId id of machine to connect to console
        result str

        """
        machine = self._getMachine(machineId)
        if machine.status != enums.MachineStatus.RUNNING:
            return None
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_get_console_url(node)

    def clone(self, machineId, name, **kwargs):
        """
        clone a machine
        param:machineId id of machine to clone
        param:name name of cloned machine
        result str

        """
        machine = self._getMachine(machineId)
        clone = machine.clone(name)
        return clone.id
