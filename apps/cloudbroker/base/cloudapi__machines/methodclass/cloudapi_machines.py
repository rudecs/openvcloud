from JumpScale import j
from JumpScale.portal.portal.auth import auth as audit
from cloudbrokerlib import authenticator, enums
import JumpScale.grid.osis
import string, time
from random import sample, choice
from libcloud.compute.base import NodeAuthPassword
import urlparse
from billingenginelib import pricing
from billingenginelib import account as accountbilling

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

        self.osisclient = j.core.osis.getClientByInstance('main')
        self.acl = j.clients.agentcontroller.get()
        self.osis_logs = j.core.osis.getClientForCategory(self.osisclient, "system", "log")
        self._pricing = pricing.pricing()
        self._accountbilling = accountbilling.account()
        self._minimum_days_of_credit_required = float(j.application.config.get("mothership1.cloudbroker.creditcheck.daysofcreditrequired"))
        self.netmgr = j.apps.jumpscale.netmgr

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
        j.logger.log(actiontype.capitalize(), category='machine.history.ui', tags=tags)
        return method(node)

    @authenticator.auth(acl='X')
    @audit()
    def start(self, machineId, **kwargs):
        return self._action(machineId, 'start', enums.MachineStatus.RUNNING)

    @authenticator.auth(acl='X')
    @audit()
    def stop(self, machineId, **kwargs):
        return self._action(machineId, 'stop', enums.MachineStatus.HALTED)

    @authenticator.auth(acl='X')
    @audit()
    def reboot(self, machineId, **kwargs):
        return self._action(machineId, 'reboot', enums.MachineStatus.RUNNING)

    @authenticator.auth(acl='X')
    @audit()
    def pause(self, machineId, **kwargs):
        return self._action(machineId, 'suspend', enums.MachineStatus.SUSPENDED)

    @authenticator.auth(acl='X')
    @audit()
    def resume(self, machineId, **kwargs):
        return self._action(machineId, 'resume', enums.MachineStatus.RUNNING)

    @authenticator.auth(acl='C')
    @audit()
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
        machine = self._getMachine(machineId)
        disk = self.models.disk.new()
        disk.name = diskName
        disk.descr = description
        disk.sizeMax = size
        disk.type = type
        self.cb.extensions.imp.addDiskToMachine(machine, disk)
        diskid = self.models.disk.set(disk)[0]
        machine.disks.append(diskid)
        self.models.vmachine.set(machine)
        return diskid

    @authenticator.auth(acl='C')
    @audit()
    def createTemplate(self, machineId, templatename, basename, **kwargs):
        """
        Creates a template from the active machine
        param:machineId id of the machine
        param:templatename name of the template
        param:basename Snapshot id on which the template is based
        result str
        """
        machine = self._getMachine(machineId)
        node = self._getNode(machine.referenceId)
        provider = self._getProvider(machine)
        cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
        image = self.models.image.new()
        image.name = templatename
        image.referenceId = ""
        image.type = 'Custom Templates'
        m = {}
        m['stackId'] = machine.stackId
        m['disks'] = machine.disks
        m['sizeId'] = machine.sizeId
        firstdisk = self.models.disk.get(machine.disks[0])
        image.size = firstdisk.sizeMax
        image.username = ""
        image.accountId = cloudspace.accountId
        image.status = 'CREATING'
        imageid = self.models.image.set(image)[0]
        stack = self.models.stack.get(machine.stackId)
        stack.images.append(imageid)
        self.models.stack.set(stack)
        provider.client.ex_createTemplate(node, templatename, imageid, basename)
        return imageid

    @authenticator.auth(acl='C')
    @audit()
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
    @audit()
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
        ctx = kwargs['ctx']
        if not self._assertName(cloudspaceId, name, **kwargs):
            ctx.start_response('409 Conflict', [])
            return 'Selected name already exists'
        if not disksize:
            raise ValueError("Invalid disksize %s" % disksize)

        
        #Check if there is enough credit
        cloudspaceId = int(cloudspaceId)
        sizeId = int(sizeId)
        imageId = int(imageId)
        accountId = self.models.cloudspace.get(cloudspaceId).accountId
        available_credit = self._accountbilling.getCreditBalance(accountId)
        burnrate = self._pricing.get_burn_rate(accountId)['hourlyCost']
        hourly_price_new_machine = self._pricing.get_price_per_hour(imageId, sizeId, disksize)
        new_burnrate = burnrate + hourly_price_new_machine
        if available_credit < (new_burnrate * 24 * self._minimum_days_of_credit_required):
            ctx.start_response('409 Conflict', [])
            return 'Not enough credit for this machine to run for %i days' % self._minimum_days_of_credit_required

        cloudspace = self.models.cloudspace.get(cloudspaceId)
        #create a public ip and virtual firewall on the cloudspace if needed
        if cloudspace.status != 'DEPLOYED':
            args = {'cloudspaceId': cloudspaceId}
            self.acl.executeJumpScript('cloudscalers', 'cloudbroker_deploycloudspace', args=args, nid=j.application.whoAmI.nid, wait=False)

        machine = self.models.vmachine.new()
        image = self.models.image.get(imageId)
        networkid = cloudspace.networkId
        machine.cloudspaceId = cloudspaceId
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId
        machine.creationTime = int(time.time())

        disk = self.models.disk.new()
        disk.name = '%s_1'
        disk.descr = 'Machine boot disk'
        disk.sizeMax = disksize
        diskid = self.models.disk.set(disk)[0]
        machine.disks.append(diskid)

        account = machine.new_account()
        if image.type == 'Custom Templates':
            account.login = 'Custom login'
            account.password = 'Custom password'
        else:
            if hasattr(image, 'username') and image.username:
                account.login = image.username
            else:
                account.login = 'cloudscalers'
            length = 6
            chars = string.letters + string.digits
            letters = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']
            passwd = ''.join(choice(chars) for _ in xrange(length))
            passwd = passwd + choice(string.digits) + choice(letters[0]) + choice(letters[1])
            account.password = passwd
        auth = NodeAuthPassword(account.password)
        machine.id = self.models.vmachine.set(machine)[0]

        try:
            stack = self.cb.extensions.imp.getBestProvider(cloudspace.gid, imageId)
            if stack == -1:
                self.models.vmachine.delete(machine.id)
                ctx = kwargs['ctx']
                ctx.start_response('503 Service Unavailable', [])
                return 'Not enough resource available to provision the requested machine'
            provider = self.cb.extensions.imp.getProviderByStackId(stack['id'])
            psize = self._getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            machine.cpus = psize.vcpus if hasattr(psize, 'vcpus') else None
            name = 'vm-%s' % machine.id
        except:
            self.models.vmachine.delete(machine.id)
            raise
        node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth, networkid=networkid)
        excludelist = [stack['id']]
        while(node == -1):
            #problem during creation of the machine on the node, we should create the node on a other machine
            stack = self.cb.extensions.imp.getBestProvider(cloudspace.gid, imageId, excludelist)
            if stack == -1:
                  self.models.vmachine.delete(machine.id)
                  ctx = kwargs['ctx']
                  ctx.start_response('503 Service Unavailable', [])
                  return 'Not enough resource available to provision the requested machine'
            excludelist.append(stack['id'])
            provider = self.cb.extensions.imp.getProviderByStackId(stack['id'])
            psize = self._getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth, networkid=networkid)
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
        self.models.vmachine.set(machine)

        cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
        providerstacks = set(cloudspace.resourceProviderStacks)
        providerstacks.add(stackId)
        cloudspace.resourceProviderStacks = list(providerstacks)
        self.models.cloudspace.set(cloudspace)

    @authenticator.auth(acl='D')
    @audit()
    def delDisk(self, machineId, diskId, **kwargs):
        """
        Delete a disk from machine
        param:machineId id of machine
        param:diskId id of disk to delete
        result bool

        """
        machine = self._getMachine(machineId)
        diskfound = diskId in machine.disks
        if diskfound:
            machine.disks.remove(diskId)
            self.models.vmachine.set(machine)
            self.models.disk.delete(diskId)
        return diskfound

    @authenticator.auth(acl='D')
    @audit()
    def delete(self, machineId, **kwargs):
        """
        Delete a machine
        param:machineId id of the machine
        result

        """
        vmachinemodel = self._getMachine(machineId)
        if not vmachinemodel.status == 'DESTROYED':
            vmachinemodel.deletionTime = int(time.time())
            vmachinemodel.status = 'DESTROYED'
            self.models.vmachine.set(vmachinemodel)

        tags = str(machineId)
        j.logger.log('Deleted', category='machine.history.ui', tags=tags)
        try:
            j.apps.cloudapi.portforwarding.deleteByVM(vmachinemodel)
        except Exception, e:
            j.errorconditionhandler.processPythonExceptionObject(e, message="Failed to delete portforwardings for vm with id %s" % machineId)

        provider, node = self._getProviderAndNode(machineId)
        if provider:
            for pnode in provider.client.list_nodes():
                if node.id == pnode.id:
                    provider.client.destroy_node(pnode)
                    break

    def _getStorage(self, machine):
        if not machine['stackId']:
            return None
        provider = self.cb.extensions.imp.getProviderByStackId(machine['stackId'])
        firstdisk = self.models.disk.get(machine['disks'][0])
        storage = provider.getSize(self.models.size.get(machine['sizeId']), firstdisk)
        return storage

    @authenticator.auth(acl='R')
    @audit()
    def get(self, machineId, **kwargs):
        """
        Get information from a certain object.
        This contains all information about the machine.
        param:machineId id of machine
        result

        """
        provider, node = self._getProviderAndNode(machineId)
        machine = self._getMachine(machineId)
        m = {}
        m['stackId'] = machine.stackId
        m['disks'] = machine.disks
        m['sizeId'] = machine.sizeId
        osImage = self.models.image.get(machine.imageId).name
        storage = self._getStorage(m)
        node = provider.client.ex_getDomain(node)
        if machine.nics and machine.nics[0].ipAddress == 'Undefined':
            cloudspace = self.models.cloudspace.get(machine.cloudspaceId)
            fwid = "%s_%s" % (cloudspace.gid, cloudspace.networkId)
            try:
                ipaddress = self.netmgr.fw_get_ipaddress(fwid, node.extra['macaddress'])
                if ipaddress:
                    machine.nics[0].ipAddress= ipaddress
                    self.models.vmachine.set(machine)
            except:
                pass # VFW not deployed yet
        return {'id': machine.id, 'cloudspaceid': machine.cloudspaceId,
                'name': machine.name, 'description': machine.descr, 'hostname': machine.hostName,
                'status': enums.MachineStatusMap.getByValue(node.state), 'imageid': machine.imageId, 'osImage': osImage, 'sizeid': machine.sizeId,
                'interfaces': machine.nics, 'storage': storage.disk, 'accounts': machine.accounts, 'locked': node.extra['locked']}

    @authenticator.auth(acl='R')
    @audit()
    def list(self, cloudspaceId, status=None, **kwargs):
        """
        List the deployed machines in a space. Filtering based on status is possible.
        param:cloudspaceId id of cloudspace in which machine exists
        param:status when not empty will filter on type types are (ACTIVE,HALTED,BACKUP,EXPORT,SNAPSHOT)
        result list

        """
        cloudspaceId = int(cloudspaceId)
        fields = ['id', 'referenceId', 'cloudspaceid', 'hostname', 'imageId', 'name', 'nics', 'sizeId', 'status', 'stackId', 'disks']
        query = {"cloudspaceId": cloudspaceId, "status": {"$ne": "DESTROYED"}}
        results = self.models.vmachine.search(query)[1:]
        machines = []
        for res in results:
            storage = self._getStorage(res)
            if storage:
                res['storage'] = storage.disk
            else:
                res['storage'] = 0
            machines.append(res)
        self.cb.extensions.imp.filter(results, fields)
        return machines

    def _getMachine(self, machineId):
        machineId = int(machineId)
        return self.models.vmachine.get(machineId)

    def _getNode(self, referenceId):
        return self.cb.extensions.imp.Dummy(id=referenceId)

    def _getProviderAndNode(self, machineId):
        machineId = int(machineId)
        machine = self._getMachine(machineId)
        provider = self._getProvider(machine)
        return provider, self.cb.extensions.imp.Dummy(id=machine.referenceId)

    @authenticator.auth(acl='C')
    @audit()
    def snapshot(self, machineId, name, **kwargs):
        """
        param:machineId id of machine to snapshot
        param:name Optional name to give snapshot
        result int
        """
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        ctx = kwargs['ctx']
        if not modelmachine.status == enums.MachineStatus.RUNNING:
            ctx.start_response('409 Conflict', [])
            return 'A snapshot can only be created from a running Machine bucket'
        snapshots = provider.client.ex_listsnapshots(node)
        if len(snapshots) > 5:
            ctx.start_response('409 Conflict', [])
            return 'Max 5 snapshots allowed'
        tags = str(machineId)
        j.logger.log('Snapshot created', category='machine.history.ui', tags=tags)
        snapshot = provider.client.ex_snapshot(node, name)
        return snapshot['name']

    @authenticator.auth(acl='C')
    @audit()
    def listSnapshots(self, machineId, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        snapshots = provider.client.ex_listsnapshots(node)
        result = []
        for snapshot in snapshots:
            if not snapshot['name'].endswith('_DELETING'):
                result.append(snapshot)
        return result

    @authenticator.auth(acl='C')
    @audit()
    def deleteSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        if not modelmachine.status == enums.MachineStatus.RUNNING:
            ctx = kwargs['ctx']
            ctx.start_response('409 Conflict', [])
            return 'A snapshot can only be removed from a running Machine bucket'
        tags = str(machineId)
        j.logger.log('Snapshot deleted', category='machine.history.ui', tags=tags)
        return provider.client.ex_snapshot_delete(node, name)

    @authenticator.auth(acl='C')
    @audit()
    def rollbackSnapshot(self, machineId, name, **kwargs):
        provider, node = self._getProviderAndNode(machineId)
        modelmachine = self._getMachine(machineId)
        if not modelmachine.status == enums.MachineStatus.HALTED:
           ctx = kwargs['ctx']
           ctx.start_response('409 Conflict', [])
           return 'A snapshot can only be rolled back to a stopped Machine bucket'
        tags = str(machineId)
        j.logger.log('Snapshot rolled back', category='machine.history.ui', tags=tags)
        return provider.client.ex_snapshot_rollback(node, name)

    @authenticator.auth(acl='C')
    @audit()
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
        #if name:
        #    if not self._assertName(machine.cloudspaceId, name, **kwargs):
        #        ctx = kwargs['ctx']
        #        ctx.start_response('409 Conflict', [])
        #        return 'Selected name already exists'
        #    machine.name = name
        if description:
            machine.descr = description
        #if size:
        #    machine.nrCU = size
        return self.models.vmachine.set(machine)[0]

    @authenticator.auth(acl='R')
    @audit()
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

    @authenticator.auth(acl='C')
    @audit()
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
            origdisk = self.models.disk.get(diskId)
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

    @authenticator.auth(acl='R')
    @audit()
    def getHistory(self, machineId, size, **kwargs):
        """
        Gets the machine actions history
        """
        tags = str(machineId)
        query = {'category': 'machine_history_ui', 'tags': tags}
        return self.osis_logs.search(query, size=size)[1:]

    @authenticator.auth(acl='R')
    @audit()
    def export(self, machineId, name, host, aws_access_key, aws_secret_key, bucket, **kwargs):
        """
        Create a export/backup of a machine
        param:machineId id of the machine to backup
        param:name Usefull name for this backup
        param:backuptype Type e.g raw, condensed
        param:host host to export(if s3)
        param:aws_access_key s3 access key
        param:aws_secret_key s3 secret key
        result jobid
        """
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        system_cl = j.core.osis.getClientForNamespace('system')
        machine = self.models.vmachine.get(machineId)
        if not machine:
            ctx.start_response('400', headers)
            return 'Machine %s not found' % machineId
        stack = self.models.stack.get(machine.stackId)
        storageparameters  = {}
        if not aws_access_key or not aws_secret_key or not host:
            ctx.start_response('400', headers)
            return 'S3 parameters are not provided'
        storageparameters['aws_access_key'] = aws_access_key
        storageparameters['aws_secret_key'] = aws_secret_key
        storageparameters['host'] = host
        storageparameters['is_secure'] = True

        storageparameters['storage_type'] = 'S3'
        storageparameters['backup_type'] = 'condensed'
        storageparameters['bucket'] = bucket
        storageparameters['mdbucketname'] = bucket

        storagepath = '/mnt/vmstor/vm-%s' % machineId
        nodes = system_cl.node.search({'name':stack.referenceId})[:1]
        if len(nodes) != 1:
            ctx.start_response('409', headers)
            return 'Incorrect model structure'
        nid = nodes[0]['id']
        args = {'path':storagepath, 'name':name, 'machineId':machineId, 'storageparameters': storageparameters,'nid':nid, 'backup_type':'condensed'}
        agentcontroller = j.clients.agentcontroller.get()
        id = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_export', j.application.whoAmI.nid, args=args, wait=False)['id']
        return id

    
    @authenticator.auth(acl='C')
    @audit()
    def importToNewMachine(self, name, cloudspaceId, vmexportId, sizeId, description, aws_access_key, aws_secret_key, **kwargs):
        """
        restore export to a new machine
        param:name name of the machine
        param:cloudspaceId id of the exportd to backup
        param:sizeId id of the specific size
        param:description optional description
        param:aws_access_key s3 access key
        param:aws_secret_key s3 secret key
        result jobid
        """
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        vmexport = self.models.vmexport.get(vmexportId)
        if not vmexport:
            ctx.start_response('400', headers)
            return 'Export definition with id %s not found' % vmexportId
        host = vmexport.server
        bucket = vmexport.bucket
        import_name = vmexport.name


        storageparameters = {}

        if not aws_access_key or not aws_secret_key:
            ctx.start_response('400', headers)
            return 'S3 parameters are not provided'

        storageparameters['aws_access_key'] = aws_access_key
        storageparameters['aws_secret_key'] = aws_secret_key
        storageparameters['host'] = host
        storageparameters['is_secure'] = True

        storageparameters['storage_type'] = 'S3'
        storageparameters['backup_type'] = 'condensed'
        storageparameters['bucket'] = bucket
        storageparameters['mdbucketname'] = bucket
        storageparameters['import_name'] = import_name

        args = {'name':name, 'cloudspaceId':cloudspaceId, 'vmexportId':vmexportId, 'sizeId':sizeId, 'description':description, 'storageparameters': storageparameters}

        agentcontroller = j.clients.agentcontroller.get()

        id = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_import_tonewmachine', j.application.whoAmI.nid, args=args, wait=False)['id']
        return id

    @authenticator.auth(acl='R')
    @audit()
    def listExports(self, machineId, status, **kwargs):
        """
        List exported images
        param:machineId id of the machine
        param:status filter on specific status
        result dict
        """
        query = {}
        if status:
            query['status'] = status
        if machineId:
            query['machineId'] = machineId
        exports = self.models.vmexport.search(query)[1:]
        exportresult = []
        for exp in exports:
            exportresult.append({'status':exp['status'], 'type':exp['type'], 'storagetype':exp['storagetype'], 'machineId': exp['machineId'], 'id':exp['id'], 'name':exp['name'],'timestamp':exp['timestamp']})
        return exportresult

