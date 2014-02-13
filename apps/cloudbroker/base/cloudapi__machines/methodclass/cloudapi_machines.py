from JumpScale import j
from cloudbrokerlib import authenticator, enums
import JumpScale.grid.osis
import string
from random import sample, choice
from libcloud.compute.base import NodeAuthPassword
import urlparse

ujson = j.db.serializers.ujson


class cloudapi_machines(object):
    """
    API Actor api, this actor is the final api a enduser uses to manage his resources

    """
    def __init__(self):

        self._te = {}
        self.actorname = "machines"
        self.appname = "cloudapi"
        self._cb = None
        self._models = None
        j.logger.setLogTargetLogForwarder()

        self.osisclient = j.core.osis.getClient(user='root')
        self.osis_logs = j.core.osis.getClientForCategory(self.osisclient, "system", "log")

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloud.cloudbroker
        return self._cb

    @property
    def models(self):
        if not self._models:
            self._models = self.cb.extensions.imp.getModel()
        return self._models

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
            self.models.vmachine.set(machine)
        tags = str(machineId)
        j.logger.log(actiontype, category='machine.history.ui', tags=tags)
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
        machine = self.models.vmachine.get(machineId)
        disk = self.cb.models.disk.new()
        disk.name = diskName
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        self.cb.extensions.imp.addDiskToMachine(machine, disk)
        diskid = self.models.disk.set(disk)[0]
        machine['disks'].append(diskid)
        self.models.vmachine.set(machine)
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

    def _assertName(self, cloudspaceId, name, **kwargs):
        for m in self.list(cloudspaceId, **kwargs):
            if m['name'] == name:
                return False
        return True
                


    def _getSize(self, provider, machine):
        brokersize = self.models.size.get(machine.sizeId)
        firstdisk = self.models.disk.get(machine.disks[0])
        return provider.getSize(brokersize, firstdisk)

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
        if not self._assertName(cloudspaceId, name, **kwargs):
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'Selected name already exists'
        if not disksize:
            raise ValueError("Invalid disksize %s" % disksize)

        machine = self.cb.models.vmachine.new()
        image = self.models.image.get(imageId)
        machine.cloudspaceId = cloudspaceId
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId

        disk = self.cb.models.disk.new()
        disk.name = '%s_1'
        disk.descr = 'Machine boot disk'
        disk.sizeMax = disksize
        diskid = self.models.disk.set(disk)[0]
        machine.disks.append(diskid)

        account = machine.new_account()
        if 'username' in image and image['username']:
            account.login = image['username']
        else:
            account.login = 'cloudscalers'
        length = 6
        chars = string.letters + string.digits
        letters = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
        passwd = ''.join(choice(chars) for _ in xrange(length))
        passwd = passwd + choice(string.digits) + choice(letters[0]) + choice(letters[1])
        account.password = passwd
        auth = NodeAuthPassword(passwd)
        machine.id = self.models.vmachine.set(machine)[0]

        try:
            stack = self.cb.extensions.imp.getBestProvider(imageId)
            provider = self.cb.extensions.imp.getProviderByStackId(stack['id'])
            psize = self._getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            machine.cpus = psize.vcpus if hasattr(psize, 'vcpus') else None
            name = 'vm-%s' % machine.id
        except:
            self.models.vmachine.delete(machine.id)
            raise
        node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth)
        excludelist = [stack['id']]
        while(node == -1):
            #problem during creation of the machine on the node, we should create the node on a other machine
            stack = self.cb.extensions.imp.getBestProvider(imageId, excludelist)
            if stack == -1:
                  self.models.vmachine.delete(machine.id)
                  ctx = kwargs['ctx']
                  ctx.start_response('503 Service Unavailable', [])
                  return 'Not enough resource available to provision the requested machine'
            excludelist.append(stack['id'])
            provider = self.cb.extensions.imp.getProviderByStackId(stack['id'])
            psize = self._getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth)
        self._updateMachineFromNode(machine, node, stack['id'], psize)
        tags = str(machine.id)
        j.logger.log('Created', category='machine.history.ui', tags=tags)
        return machine.id

    def _updateMachineFromNode(self, machine, node, stackId, psize):
        machine.referenceId = node.id
        machine.referenceSizeId = psize.id
        machine.stackId = stackId
        machine.status = enums.MachineStatus.RUNNING
        machine.hostName = node.name
        for ipaddress in node.public_ips:
            nic = machine.new_nic()
            nic.ipAddress = ipaddress
        self.models.vmachine.set(machine.obj2dict())

        cloudspace = self.cb.models.cloudspace.new()
        cloudspace.dict2obj(self.models.cloudspace.get(machine.cloudspaceId))
        cloudspace.resourceProviderStacks.append(stackId)
        self.models.cloudspace.set(cloudspace)

    @authenticator.auth(acl='D')
    def delDisk(self, machineId, diskId, **kwargs):
        """
        Delete a disk from machine
        param:machineId id of machine
        param:diskId id of disk to delete
        result bool

        """
        machine = self.models.vmachine.get(machineId)
        diskfound = diskId in machine['disks']
        if diskfound:
            machine['disks'].remove(diskId)
            self.models.vmachine.set(machine)
            self.models.disk.delete(diskId)
        return diskfound

    @authenticator.auth(acl='D')
    def delete(self, machineId, **kwargs):
        """
        Delete a machine
        param:machineId id of the machine
        result

        """
        vmachinemodel = self.models.vmachine.get(machineId)
        vmachinemodel['status'] = 'DESTROYED'
        self.models.vmachine.set(vmachinemodel)
        provider, node = self._getProviderAndNode(machineId)
        if provider:
            for pnode in provider.client.list_nodes():
                if node.id == pnode.id:
                    provider.client.destroy_node(pnode)
                    break
        tags = str(machineId)
        j.logger.log('Deleted', category='machine.history.ui', tags=tags)
        return self.models.vmachine.delete(machineId)

    def exporttoremote(self, machineId, exportName, uncpath, emailaddress, **kwargs):
        """
        param:machineId id of machine to export
        param:exportName give name to export action
        param:uncpath unique path where to export machine to ()
        param:emailaddress to this address the result of the export is send.
        result boolean if export is successfully started
        """
        provider, node = self._getProviderAndNode(machineId)
        elements = urlparse.urlparse(uncpath)
        if not elements.scheme in ['cifs','smb','ftp','file','sftp','http']:
            ctx = kwargs['ctx']
            ctx.start_response('400 Bad Request', [])
            return 'Incorrect uncpath format, only cifs, smb, ftp, file, sftp and http is supported'
        started = provider.client.ex_export(node, exportName, uncpath, emailaddress)
        if started:
            return True
        else:
            return False

    def _getStorage(self, machine):
        if not machine['stackId'] or machine['stackId'] == 0:
            return None
        provider = self.cb.extensions.imp.getProviderByStackId(machine['stackId'])
        firstdisk = self.models.disk.get(machine['disks'][0])
        storage = provider.getSize(self.models.size.get(machine['sizeId']), firstdisk)
        return storage

    @authenticator.auth(acl='R')
    def get(self, machineId, **kwargs):
        """
        Get information from a certain object.
        This contains all information about the machine.
        param:machineId id of machine
        result

        """
        machine = self.models.vmachine.get(machineId)
        storage = self._getStorage(machine)
        return {'id': machine['id'], 'cloudspaceid': machine['cloudspaceId'],
                'name': machine['name'], 'hostname': machine['hostName'],
                'status': machine['status'], 'imageid': machine['imageId'], 'sizeid': machine['sizeId'],
                'interfaces': machine['nics'], 'storage': storage.disk, 'accounts': machine['accounts']}

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
        query = {'fields': ['id', 'referenceId', 'cloudspaceid', 'hostname', 'imageId', 'name', 'nics', 'sizeId', 'status', 'stackId', 'disks']}
        if term:
            query['query'] = {'term': term}
        results = self.models.vmachine.find(ujson.dumps(query))['result']
        machines = []
        for res in results:
            storage = self._getStorage(res['fields'])
            if storage:
                res['fields']['storage'] = storage.disk
            else:
                res['fields']['storage'] = 0
            machines.append(res['fields'])
        return machines

    def _getMachine(self, machineId):
        machine = self.cb.models.vmachine.new()
        machine.dict2obj(self.models.vmachine.get(machineId))
        return machine

    def _getNode(self, referenceId):
        return self.cb.extensions.imp.Dummy(id=referenceId)

    def _getProviderAndNode(self, machineId):
        machine = self._getMachine(machineId)
        provider = self._getProvider(machine)
        return provider, self.cb.extensions.imp.Dummy(id=machine.referenceId)

    @authenticator.auth(acl='C')
    def snapshot(self, machineId, name, **kwargs):
        """
        param:machineId id of machine to snapshot
        param:name Optional name to give snapshot
        result int
        """
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        if not modelmachine.status == enums.MachineStatus.HALTED:
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'A snapshot can only be created from a running Machine bucket'
        tags = str(machineId)
        j.logger.log('Snapshot created', category='machine.history.ui', tags=tags)
        snapshot = provider.client.ex_snapshot(node, name)
        return snapshot['name']

    @authenticator.auth(acl='C')
    def listSnapshots(self, machineId, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        return provider.client.ex_listsnapshots(node)

    @authenticator.auth(acl='C')
    def deleteSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        if not modelmachine.status == enums.MachineStatus.HALTED:
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'A snapshot can only be removed from a running Machine bucket'
        tags = str(machineId)
        j.logger.log('Snapshot deleted', category='machine.history.ui', tags=tags)
        return provider.client.ex_snapshot_delete(node, name)

    @authenticator.auth(acl='C')
    def rollbackSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        if not modelmachine.status == enums.MachineStatus.HALTED:
           ctx = kwargs['ctx']
           ctx.start_response('409 Conflict', [])
           return 'A snapshot can only be rolled back to a stopped Machine bucket'
        tags = str(machineId)
        j.logger.log('Sanpshot rolled back', category='machine.history.ui', tags=tags)
        return provider.client.ex_snapshot_rollback(node, name)

    @authenticator.auth(acl='W')
    def update(self, machineId, name=None, description=None, size=None, **kwargs):
        """
        Change basic properties of a machine.
        Name, description can be changed with this action.
        param:machineId id of the machine
        param:name name of the machine
        param:description description of the machine
        param:size size of the machine in CU

        """
        machine = self._getMachine(machineId)
        if name:
            if not self._assertName(cloudspaceId, name, **kwargs):
                ctx = kwargs['ctx']
                ctx.start_response('409 Conflict', [])
                return 'Selected name already exists'
            machine.name = name
        if description:
            machine.description = description
        if size:
            machine.nrCU = size
        return self.models.vmachine.set(machine)[0]

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
        if not machine.status == enums.MachineStatus.HALTED:
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'A clone can only be taken from a stopped machine bucket'
        if machine.clone or machine.cloneReference:
            ctx = kwargs['ctx']
            ctx.start_response('405 Method not Allowed', [])
            return 'This machine has already a clone or is a clone or has been cloned in the past'

        if not self._assertName(machine.cloudspaceId, name, **kwargs):
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'Selected name already exists'
        clone = self.cb.models.vmachine.new()
        clone.cloudspaceId = machine.cloudspaceId
        clone.name = name
        clone.descr = machine.descr
        clone.sizeId = machine.sizeId
        clone.imageId = machine.imageId
        clone.cloneReference = machine.id

        for diskId in machine.disks:
            origdisk = self.cb.models.disk.new()
            origdisk.dict2obj(self.models.disk.get(diskId))
            clonedisk = self.cb.models.disk.new()
            clonedisk.name = origdisk.name
            clonedisk.descr = origdisk.descr
            clonedisk.sizeMax = origdisk.sizeMax
            clonediskId = self.models.disk.set(clonedisk)[0]
            clone.disks.append(clonediskId)
        clone.id = self.models.vmachine.set(clone)[0]
        provider, node = self._getProviderAndNode(machineId)
        name = 'vm-%s' % clone.id
        size = self._getSize(provider, clone)
        node = provider.client.ex_clone(node, size, name)
        machine.clone = clone.id
        self.models.vmachine.set(machine)
        self._updateMachineFromNode(clone, node, machine.stackId, size)
        tags = str(machineId)
        j.logger.log('Cloned', category='machine.history.ui', tags=tags)
        return clone.id

    def getHistory(self, machineId, size, **kwargs):
        """
        Gets the machine actions history
        """
        tags = str(machineId)
        query = {"query": {"bool": {"must": [{"term": {"category": "machine_history_ui"}}, {"term": {"tags": tags}}]}}, "size": size}
        return self.osis_logs.search(query)['hits']['hits']
