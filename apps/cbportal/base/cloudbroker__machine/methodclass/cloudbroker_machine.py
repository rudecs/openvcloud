from JumpScale import j
import time, string
from random import choice
from libcloud.compute.base import NodeAuthPassword
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth
import urllib
import urlparse
import JumpScale.baselib.remote.cuisine

class cloudbroker_machine(j.code.classGetBase()):
    def __init__(self):
        self._te={}
        self.actorname="machine"
        self.appname="cloudbroker"
        self.cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        self.libvirtcl = j.core.osis.getClientForNamespace('libvirt')
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

    @auth(['level1','level2'])
    def liveMigrate(self, accountName, machineId, cpuNodeName, stackId, **kwargs):
        if not self.cbcl.vmachine.exists(machineId):
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'Machine ID %s was not found' % machineId

        vmachine = self.cbcl.vmachine.get(machineId)
        cloudspace = self.cbcl.cloudspace.get(vmachine.cloudspaceId)
        account = self.cbcl.account.get(cloudspace.accountId)
        if not account.name == accountName:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('400', headers)
            return "Machine's account %s does not match the given account name %s" % (account.name, accountName)

        # TODO: Check if space is on current grid

        stacks = self.cbcl.stack.simpleSearch({'id': stackId, 'referenceId': cpuNodeName})
        if not stacks:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return 'Target node %s whose stackId %s was not found' % (cpuNodeName, stackId)

        target_stack = stacks[0]
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
            if not target_api.file_md5(image_path) == source_api.file_md5(image_path):
                ctx = kwargs['ctx']
                headers = [('Content-Type', 'application/json'), ]
                ctx.start_response('400', headers)
                return "Image's MD5sum on target node doesn't match machine base image MD5sum"
        else:
            ctx = kwargs['ctx']
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response('404', headers)
            return "Machine base image was not found on target node"

        def _create_network():
            from JumpScale.lib import ovsnetconfig
            import libvirt
            networkname = 'space_%s' % cloudspace.networkId
            vxnet = j.system.ovsnetconfig.ensureVXNet(cloudspace.networkId, 'vxbackend')
            bridgename = vxnet.bridge.name
            networkxml = """<network>
            <name>%s</name>
                <forward mode='bridge'/>
                <bridge name='%s'/>
                <virtualport type='openvswitch'/>
            </network>"""% (networkname, bridgename)
            connection = libvirt.open(target_stack['apiUrl'])
            connection.networkCreateXML(networkxml)

        # REWORK: do not assume disks on same node, they are on remote cpu node
        def _create_disks():
            import JumpScale.lib.qemu_img
            def _create_disk(disk):
                disk_info = j.system.platform.qemu_img.info(disk)
                if 'backing file' in disk_info:
                    if target_api.file_exists(disk_info['backing file']):
                        if not target_api.file_exists(disk_info['image']):
                            disk_data = {'disk_image': disk_info['image'], 'size': disk_info['virtual size'], 'base': disk_info['backing file']}
                            target_api.run('qemu-img create -f qcow2 %(disk_image)s %(size)s -b %(base)s' % disk_data)
                    else:
                        _create_disk(disk_info['backing file'])
                        _create_disk(disk)

            target_api.dir_ensure(j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vmachine.id), True)
            disks = j.system.fs.listFilesInDir(j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vmachine.id))
            for disk in disks:
                _create_disk(disk)

        _create_network()
        _create_disks()

        iso_file_path = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % vmachine.id, 'cloud-init.vm-%s.iso' % vmachine.id)
        target_api.file_upload(iso_file_path, iso_file_path, scp=True)

        # TODO: Migrate snapshots

        source_api.run('virsh migrate --live %s %s --copy-storage-inc --verbose --persistent --undefinesource' % (vmachine.id, target_stack['apiUrl']))