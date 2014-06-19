from JumpScale import j
import time, string
from random import choice
from libcloud.compute.base import NodeAuthPassword
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import urllib,ujson
import urlparse
import JumpScale.baselib.remote.cuisine
import JumpScale.grid.agentcontroller


class cloudbroker_machine(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="machine"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.libvirtcl = j.core.osis.getClientForNamespace('libvirt')
        self._cb = None
        self.machines_actor = self.cb.extensions.imp.actors.cloudapi.machines
        self.acl = j.clients.agentcontroller.get()

    @property
    def cb(self):
        if not self._cb:
            self._cb = j.apps.cloudbroker.iaas
        return self._cb

    @auth(['level1',])
    def createOnStack(self, cloudspaceId, name, description, sizeId, imageId, disksize, stackid, **kwargs):
        """
        Create a machine on a specific stackid
        param:cloudspaceId id of space in which we want to create a machine
        param:name name of machine
        param:description optional description
        param:sizeId id of the specific size
        param:imageId id of the specific image
        param:disksize size of base volume
        param:stackid id of the stack
        result bool
        """
        location = j.application.config.get('cloudbroker.where.am.i')
        machine = self.cbcl.vmachine.new()
        image = self.cbcl.image.get(imageId)
        cloudspace = self.cbcl.cloudspace.get(cloudspaceId)

        if str(cloudspace.location) != location:
            ctx = kwargs["ctx"]
            urlparts = urlparse.urlsplit(ctx.env['HTTP_REFERER'])
            params = {'cloudspaceId': cloudspaceId, 'name': name, 'description': description, 'sizeId': sizeId, 
                     'imageId': imageId, 'disksize': disksize, 'stackid': stackid}
            hostname = j.application.config.getDict('cloudbroker.location.%s' % str(cloudspace.location))['url']
            url = '%s://%s%s?%s' % (urlparts.scheme, hostname, ctx.env['PATH_INFO'], urllib.urlencode(params))
            headers = [('Content-Type', 'application/json'), ('Location', url)]
            ctx.start_response("302", headers)
            return url

        networkid = cloudspace.networkId
        machine.cloudspaceId = cloudspaceId
        machine.descr = description
        machine.name = name
        machine.sizeId = sizeId
        machine.imageId = imageId
        machine.creationTime = int(time.time())

        disk = self.cbcl.disk.new()
        disk.name = '%s_1'
        disk.descr = 'Machine boot disk'
        disk.sizeMax = disksize
        diskid = self.cbcl.disk.set(disk)[0]
        machine.disks.append(diskid)

        account = machine.new_account()
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
        auth = NodeAuthPassword(passwd)
        machine.id = self.cbcl.vmachine.set(machine)[0]

        try:
            provider = self.cb.extensions.imp.getProviderByStackId(stackid)
            psize = self._getSize(provider, machine)
            image, pimage = provider.getImage(machine.imageId)
            machine.cpus = psize.vcpus if hasattr(psize, 'vcpus') else None
            name = 'vm-%s' % machine.id
        except:
            self.cbcl.vmachine.delete(machine.id)
            raise
        node = provider.client.create_node(name=name, image=pimage, size=psize, auth=auth, networkid=networkid)
        if node == -1:
            raise
        self._updateMachineFromNode(machine, node, stackid, psize)
        return machine.id

    def _getSize(self, provider, machine):
        brokersize = self.cbcl.size.get(machine.sizeId)
        firstdisk = self.cbcl.disk.get(machine.disks[0])
        return provider.getSize(brokersize, firstdisk)

    def _updateMachineFromNode(self, machine, node, stackId, psize):
        machine.referenceId = node.id
        machine.referenceSizeId = psize.id
        machine.stackId = stackId
        machine.status = 'RUNNING'
        machine.hostName = node.name
        for ipaddress in node.public_ips:
            nic = machine.new_nic()
            nic.ipAddress = ipaddress
        self.cbcl.vmachine.set(machine)

        cloudspace = self.cbcl.cloudspace.get(machine.cloudspaceId)
        providerstacks = set(cloudspace.resourceProviderStacks)
        providerstacks.add(stackId)
        cloudspace.resourceProviderStacks = list(providerstacks)
        self.cbcl.cloudspace.set(cloudspace)

    @auth(['level1','level2'])
    def destroy(self, accountName, spaceName, machineId, reason, **kwargs):
        if not self.cbcl.vmachine.exists(machineId):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'Machine ID %s was not found' % machineId

        vmachine = self.cbcl.vmachine.get(machineId)
        cloudspace = self.cbcl.cloudspace.get(vmachine.cloudspaceId)
        if not cloudspace.name == spaceName:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return "Machine's cloudspace %s does not match the given space name %s" % (cloudspace.name, spaceName)

        account = self.cbcl.account.get(cloudspace.accountId)
        if not account.name == accountName:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return "Machine's account %s does not match the given account name %s" % (account.name, accountName)

        location = j.application.config.get('cloudbroker.where.am.i')
        if not cloudspace.location == location:
            ctx = kwargs['ctx']
            urlparts = urlparse.urlsplit(ctx.env['HTTP_REFERER'])
            params = {'accountName': accountName, 'spaceName': spaceName, 'machineId': machineId, 'reason': reason}
            hostname = j.application.config.getDict('cloudbroker.location.%s' % cloudspace.location)['url']
            url = '%s://%s%s?%s' % (urlparts.scheme, hostname, ctx.env['PATH_INFO'], urllib.urlencode(params))
            headers = [('Content-Type', 'application/json'), ('Location', url)]
            ctx.start_response('302', headers)
            return url

        self.machines_actor.delete(vmachine.id)
        return True

    @auth(['level1','level2'])
    def moveToDifferentComputeNode(self, accountName, machineId, targetComputeNode=None, withSnapshots=True, collapseSnapshots=False, **kwargs):
        if not self.cbcl.vmachine.exists(machineId):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'Machine ID %s was not found' % machineId

        vmachine = self.cbcl.vmachine.get(machineId)
        cloudspace = self.cbcl.cloudspace.get(vmachine.cloudspaceId)
        account = self.cbcl.account.get(cloudspace.accountId)
        if account.name != accountName:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return "Machine's account %s does not match the given account name %s" % (account.name, accountName)

        if targetComputeNode:
            stacks = self.cbcl.stack.simpleSearch({'referenceId': targetComputeNode})
            if not stacks:
                ctx = kwargs['ctx']
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response('404', headers)
                return 'Target node %s was not found' % targetComputeNode
            target_stack = stacks[0]
        else:
            target_stack = self.cb.extensions.imp.getBestProvider(vmachine.imageId)

        location = j.application.config.get('cloudbroker.where.am.i')
        if cloudspace.location != location:
            ctx = kwargs['ctx']
            urlparts = urlparse.urlsplit(ctx.env['HTTP_REFERER'])
            params = {'accountName': accountName, 'machineId': machineId, 'targetComputeNode': targetComputeNode,
                      'withSnapshots': withSnapshots, 'collapseSnapshots': collapseSnapshots}
            hostname = j.application.config.getDict('cloudbroker.location.%s' % cloudspace.location)['url']
            url = '%s://%s%s?%s' % (urlparts.scheme, hostname, ctx.env['PATH_INFO'], urllib.urlencode(params))
            headers = [('Content-Type', 'application/json'), ('Location', url)]
            ctx.start_response('302', headers)
            return url

        source_stack = self.cbcl.stack.get(vmachine.stackId)

        # validate machine template is on target node
        image = self.cbcl.image.get(vmachine.imageId)
        libvirt_image = self.libvirtcl.image.get(image.referenceId)
        image_path = j.system.fs.joinPaths('/mnt', 'vmstor', 'templates', libvirt_image.UNCPath)

        source_api = j.remote.cuisine.api
        source_api.connect(source_stack.referenceId)

        target_api = j.remote.cuisine.api
        target_api.connect(target_stack['referenceId'])

        if target_api.file_exists(image_path):
            if target_api.file_md5(image_path) != source_api.file_md5(image_path):
                ctx = kwargs['ctx']
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response('400', headers)
                return "Image's MD5sum on target node doesn't match machine base image MD5sum"
        else:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return "Machine base image was not found on target node"

        # create network on target node
        self.acl.executeJumpScript('cloudscalers', 'createnetwork', args={'networkid': cloudspace.networkId}, role=target_stack['referenceId'], wait=True)

        # get disks info on source node
        disks_info = self.acl.executeJumpScript('cloudscalers', 'vm_livemigrate_getdisksinfo', args={'vmId': vmachine.id}, role=source_stack.referenceId, wait=True)['result']

        # create disks on target node
        self.acl.executeJumpScript('cloudscalers', 'vm_livemigrate_createdisks', args={'vm_id': vmachine.id, 'disks_info': disks_info}, role=target_stack['referenceId'], wait=True)

        # scp the .iso file
        iso_file_path = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vmachine.id, 'cloud-init.vm-%s.iso' % vmachine.id)
        source_api.run('scp %s root@%s:%s' % (iso_file_path, target_stack['referenceId'], iso_file_path))

        if withSnapshots:
            snapshots = self.machines_actor.listSnapshots(vmachine.id)
            if snapshots:
                source_api.run('virsh dumpxml vm-%(vmid)s > /tmp/vm-%(vmid)s.xml' % {'vmid': vmachine.id})
                source_api.run('scp /tmp/vm-%(vmid)s.xml %(targethost)s:/tmp/vm-%(vmid)s.xml' % {'vmid': vmachine.id, 'targethost': target_stack['referenceId']})
                target_api.run('virsh define /tmp/vm-%s.xml' % vmachine.id)
                for snapshot in snapshots:
                    source_api.run('virsh snapshot-dumpxml %(vmid)s %(ssname)s > /tmp/snapshot_%(vmid)s_%(ssname)s.xml' % {'vmid': vmachine.id, 'ssname': snapshot['name']})
                    source_api.run('scp /tmp/snapshot_%(vmid)s_%(ssname)s.xml %(targethost)s:/tmp/snapshot_%(vmid)s_%(ssname)s.xml' % {'vmid': vmachine.id, 'ssname': snapshot['name'], 'targethost': target_stack['referenceId']})
                    target_api.run('virsh snapshot-create --redefine %(vmid)s /tmp/snapshot_%(vmid)s_%(ssname)s.xml' % {'vmid': vmachine.id, 'ssname': snapshot['name']})

        source_api.run('virsh migrate --live %s %s --copy-storage-inc --verbose --persistent --undefinesource' % (vmachine.id, target_stack['apiUrl']))
        vmachine.stackId = target_stack['id']
        self.cbcl.vmachine.set(vmachine)

    def export(self, machineId, name, backuptype, storage, host, aws_access_key, aws_secret_key,bucketname,**kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        system_cl = j.core.osis.getClientForNamespace('system')
        machine = self.cbcl.vmachine.get(machineId)
        if not machine:
            ctx.start_response('400', headers)
            return 'Machine %s not found' % machineId
        stack = self.cbcl.stack.get(machine.stackId)
        storageparameters  = {}
        if storage == 'S3':
            if not aws_access_key or not aws_secret_key or not host:
                  ctx.start_response('400', headers)
                  return 'S3 parameters are not provided'
            storageparameters['aws_access_key'] = aws_access_key
            storageparameters['aws_secret_key'] = aws_secret_key
            storageparameters['host'] = host
            storageparameters['is_secure'] = True

        storageparameters['storage_type'] = storage
        storageparameters['backup_type'] = backuptype
        storageparameters['bucket'] = bucketname
        storageparameters['mdbucketname'] = bucketname

        storagepath = '/mnt/vmstor/vm-%s' % machineId
        nodes = system_cl.node.simpleSearch({'name':stack.referenceId})
        if len(nodes) != 1:
            ctx.start_response('409', headers)
            return 'Incorrect model structure'
        nid = nodes[0]['id']
        args = {'path':storagepath, 'name':name, 'machineId':machineId, 'storageparameters': storageparameters,'nid':nid, 'backup_type':backuptype}
        id = self.acl.executeJumpScript('cloudscalers', 'cloudbroker_export', j.application.whoAmI.nid, args=args, wait=False)['result']
        return id


    def restore(self, vmexportId, nid, destinationpath, aws_access_key, aws_secret_key, **kwargs):
        ctx = kwargs['ctx']
        headers = [('Content-Type', 'application/json'), ]
        vmexport = self.cbcl.vmexport.get(vmexportId)
        if not vmexport:
            ctx.start_response('400', headers)
            return 'Export definition with id %s not found' % vmexportId
        storageparameters = {}

        if vmexport.storagetype == 'S3':
            if not aws_access_key or not aws_secret_key:
                ctx.start_response('400', headers)
                return 'S3 parameters are not provided'
            storageparameters['aws_access_key'] = aws_access_key
            storageparameters['aws_secret_key'] = aws_secret_key
            storageparameters['host'] = vmexport.server
            storageparameters['is_secure'] = True

        storageparameters['storage_type'] = vmexport.storagetype
        storageparameters['bucket'] = vmexport.bucket
        storageparameters['mdbucketname'] = vmexport.bucket


        metadata = ujson.loads(vmexport.files)

        args = {'path':destinationpath, 'metadata':metadata, 'storageparameters': storageparameters,'nid':nid}

        id = self.acl.executeJumpScript('cloudscalers', 'cloudbroker_import', j.application.whoAmI.nid, args=args, wait=False)['result']
        return id

        
    def listExports(self, status, machineId ,**kwargs):
        query = {}
        if status:
            query['status'] = status
        if machineId:
            query['machineId'] = machineId
        exports = self.cbcl.vmexport.simpleSearch(query)
        exportresult = []
        for exp in exports:
            exportresult.append({'status':exp['status'], 'type':exp['type'], 'storagetype':exp['storagetype'], 'machineId': exp['machineId'], 'id':exp['id'], 'name':exp['name'],'timestamp':exp['timestamp']})
        return exportresult


    def tag(self, machineId, tagName, **kwargs):
        """
        Adds a tag to a machine, useful for indexing and following a (set of) machines
        param:machineId id of the machine to tag
        param:tagName tag
        """
        if not self.cbcl.vmachine.exists(machineId):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'vMachine ID %s was not found' % machineId

        vmachine = self.cbcl.vmachine.get(machineId)
        tags = j.core.tags.getObject(vmachine.tags)
        if tags.labelExists(tagName):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return 'Tag %s is already assigned to this vMachine' % tagName

        tags.labelSet(tagName)
        vmachine.tags = tags.tagstring
        self.cbcl.vmachine.set(vmachine)
        return True

    def untag(self, machineId, tagName, **kwargs):
        """
        Removes a specific tag from a machine
        param:machineId id of the machine to untag
        param:tagName tag
        """
        if not self.cbcl.vmachine.exists(machineId):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'vMachine ID %s was not found' % machineId

        vmachine = self.cbcl.vmachine.get(machineId)
        tags = j.core.tags.getObject(vmachine.tags)
        if not tags.labelExists(tagName):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return 'vMachine does not have tag %s' % tagName

        tags.labelDelete(tagName)
        vmachine.tags = tags.tagstring
        self.cbcl.vmachine.set(vmachine)
        return True


    def list(self, tag=None, computeNode=None, accountName=None, cloudspaceId=None, **kwargs):
        """
        List the undestroyed machines based on specific criteria
        At least one of the criteria needs to be passed
        param:tag a specific tag
        param:computenode name of a specific computenode
        param:accountname specific account
        param:cloudspaceId specific cloudspace
        """
        if not tag and not computeNode and not accountName and not cloudspaceId:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return 'At least one parameter must be passed'
        params = dict()
        native_query = dict() 
        if tag:
            params['tags'] = tag
        if computeNode:
            stacks = self.cbcl.stack.simpleSearch({'referenceId': computeNode})
            if stacks:
                stack_id = stacks[0]['id']
                params['stackId'] = stack_id
            else:
                return list()
        if accountName:
            accounts = self.cbcl.account.simpleSearch({'name': accountName})
            if accounts:
                account_id = accounts[0]['id']
                cloudspaces = self.cbcl.cloudspace.simpleSearch({'accountId': account_id})
                if cloudspaces:
                    cloudspaces_ids = [cs['id'] for cs in cloudspaces]
                    native_query = {'query': {'bool': {'must': [{'terms': {'cloudspaceId': cloudspaces_ids}}]}}}
                else:
                    return list()
            else:
                return list()
        if cloudspaceId:
            params['cloudspaceId'] = cloudspaceId

        if not native_query:
            native_query = {'query': {'bool': {'must': []}}}

        native_query['query']['bool']['must_not'] = [{'term': {'status': 'destroyed'}}]
        return self.cbcl.vmachine.simpleSearch(params, nativequery=native_query)

    def checkImageChain(self, machineId, **kwargs):
        """
        Checks on the computenode the vm is on if the vm image is there
        Check the chain of the vmimage to see if parents are there (the template starting from)
        (executes the vm.hdcheck jumpscript)
        param:machineId id of the machine
        result dict,,
        """
        #put your code here to implement this method
        raise NotImplementedError ("not implemented method checkImageChain")
