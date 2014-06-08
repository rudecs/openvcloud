from JumpScale import j
import time, string
from random import choice
from libcloud.compute.base import NodeAuthPassword
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import urllib
import urlparse

class cloudbroker_machine(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="machine"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self._cb = None

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
