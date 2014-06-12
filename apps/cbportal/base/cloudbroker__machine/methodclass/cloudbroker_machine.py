from JumpScale import j
import time, string
from random import choice
from libcloud.compute.base import NodeAuthPassword
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import urllib,ujson
import urlparse


class cloudbroker_machine(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="machine"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self._cb = None
        self.machines_actor = self.cb.extensions.imp.actors.cloudapi.machines

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


    def export(self, machineId, name, backuptype, storage, host, aws_access_key, aws_secret_key, **kwargs):
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
        storageparameters['bucket'] = 'backup'
        storageparameters['mdbucketname'] = 'export_md'

        storagepath = '/mnt/vmstor/vm-%s' % machineId
        nodes = system_cl.node.simpleSearch({'name':stack.referenceId})
        if len(nodes) != 1:
            ctx.start_response('409', headers)
            return 'Incorrect model structure'
        nid = nodes[0]['id']
        args = {'path':storagepath, 'name':name, 'machineId':machineId, 'storageparameters': storageparameters,'nid':nid, 'backup_type':backuptype}
        agentcontroller = j.clients.agentcontroller.get()
        id = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_export', j.application.whoAmI.nid, args=args, wait=False)['id']
        return id


    def importbackup(self, vmexportId, nid, destinationpath, aws_access_key, aws_secret_key, **kwargs):
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

        metadata = ujson.loads(vmexport.files)

        args = {'path':destinationpath, 'metadata':metadata, 'storageparameters': storageparameters,'nid':nid}

        agentcontroller = j.clients.agentcontroller.get()

        id = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_import', j.application.whoAmI.nid, args=args, wait=False)['id']
        return id

        
    def listExports(self):
        return []







        
