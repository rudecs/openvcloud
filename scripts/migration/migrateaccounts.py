from gevent import monkey
monkey.patch_all()

from JumpScale import j
from xml.etree import ElementTree
from gevent.pool import Pool
import urlparse
import sys
sys.path.append('/opt/code/github/0-complexity/openvcloud/apps/cloudbroker')
j.db.serializers.getSerializerType('j')


class MaskClass(object):
    def __init__(self, *args, **kwargs):
        pass


class Migrator(object):
    def __init__(self, debug=False, dryrun=False, concurrency=1):
        self.acl = j.clients.agentcontroller.getByInstance('main')
        self.source_osis = j.clients.osis.getByInstance('source')
        self.osis = j.clients.osis.getByInstance('main')
        self.source_ccl = j.clients.osis.getNamespace('cloudbroker', self.source_osis)
        self.source_lcl = j.clients.osis.getNamespace('libcloud', self.source_osis)
        self.souce_scl = j.clients.osis.getNamespace('system', self.source_osis)
        self.source_vfw = j.clients.osis.getNamespace('vfw', self.source_osis)
        self.ccl = j.clients.osis.getNamespace('cloudbroker', self.osis)
        self.scl = j.clients.osis.getNamespace('system', self.osis)
        self.vfw = j.clients.osis.getNamespace('vfw', self.osis)
        self.concurrency = concurrency
        self.debug = debug
        self.dryrun = dryrun
        self._rgid = None
        from cloudbrokerlib import cloudbroker
        cloudbroker.models = self.ccl
        cloudbroker.CloudSpace = MaskClass
        j.apps = MaskClass()
        j.apps.system = MaskClass()
        j.apps.system.contentmanager = MaskClass()
        j.apps.system.contentmanager.getActors = lambda *a: ['libloud_libvirt']
        self.rcb = cloudbroker.CloudBroker()

    def info(self, msg, depth=0):
        if depth:
            print '  ' * depth,
        j.console.info(msg)

    @property
    def rgid(self):
        if self._rgid is None:
            self._rgid = self.ccl.location.search({})[1]['gid']
        return self._rgid

    def migrate_account(self, accountId):
        account = self.source_ccl.account.get(accountId)
        self.info('Migrating account {}'.format(account.name))
        # search if account already exists
        accounts = self.ccl.account.search({'name': account.name, 'status': {'$ne': 'DESTROYED'}})[1:]
        if not accounts:
            newaccount = self.empty(account, self.source_ccl.account.new)
            if not self.dryrun:
                newaccount.id, _, _ = self.ccl.account.set(newaccount)
        else:
            newaccount = self.ccl.account.get(accounts[0]['id'])
        for cloudspace in self.source_ccl.cloudspace.search({'accountId': accountId, 'status': 'DEPLOYED'})[1:]:
            cloudspace = self.source_ccl.cloudspace.get(cloudspace['id'])
            self.migrate_space(cloudspace, newaccount)
        account.status = 'DESTROYED'
        if not self.dryrun:
            self.source_ccl.account.set(account)

    def empty(self, obj, newmethod):
        newobj = newmethod()
        newobj.load(obj.dump())
        newobj.id = None
        newobj.guid = None
        if self.debug:
            newobj.name += '_migrated'
        return newobj

    def migrate_space(self, cloudspace, newaccount):
        self.info('Migrating space {}'.format(cloudspace.name), 1)
        cloudspaces = self.ccl.cloudspace.search({
            'name': cloudspace.name,
            'status': {'$ne': 'DESTROYED'},
            'accountId': newaccount.id,
            'networkId': cloudspace.networkId,
            'gid': self.rgid
        })[1:]
        if not cloudspaces:
            newcloudspace = self.empty(cloudspace, self.ccl.cloudspace.new)
        else:
            newcloudspace = self.ccl.cloudspace.get(cloudspaces[0]['id'])
        newcloudspace.accountId = newaccount.id
        newcloudspace.gid = self.rgid
        if not self.dryrun:
            newcloudspace.id, _, _ = self.ccl.cloudspace.set(newcloudspace)
        self.migrate_routeros(cloudspace, newcloudspace)
        vms = self.source_ccl.vmachine.search({
            'status': {'$nin': ['ERROR', 'DESTROYED']},
            'cloudspaceId': cloudspace.id
        })[1:]
        pool = Pool(self.concurrency)
        jobs = []
        for vm in vms:
            vm = self.source_ccl.vmachine.get(vm['id'])
            jobs.append(pool.apply_async(self.migrate_vm, (vm, newcloudspace)))
        for job in jobs:
            job.join()
        for job in jobs:
            job.get()

        cloudspace.status = 'DESTROYED'
        if not self.dryrun:
            self.source_ccl.cloudspace.set(cloudspace)

    def get_source_ip(self, nid):
        node = self.souce_scl.node.get(nid)
        for net in node.netaddr:
            if net['name'] == 'backplane1':
                return net['ip'][0]

    def migrate_routeros(self, originalspace, newspace):
        vfwid = '{}_{}'.format(originalspace.gid, originalspace.networkId)
        lvfw = self.source_vfw.virtualfirewall.get(vfwid)
        sourceip = self.get_source_ip(lvfw.nid)
        args = {
            'sourceip': sourceip,
            'vlan': lvfw.vlan,
            'networkid': lvfw.id
        }
        excludelist = []
        if originalspace.gid == self.rgid:
            stack = self.source_ccl.stack.search({'referenceId': str(lvfw.nid)})[1]
            excludelist.append(stack['id'])

        provider = self.rcb.getBestProvider(self.rgid, excludelist=excludelist)
        self.info('Migrating routeros to {}'.format(provider['name']), 2)
        if not self.dryrun:
            job = self.acl.executeJumpscript(
                'jumpscale',
                'vfs_migrate_routeros',
                nid=int(provider['referenceId']),
                queue='hypervisor',
                gid=self.rgid,
                args=args)
            if job['state'] != 'OK':
                raise RuntimeError("Could not execute live migrate for ros, error was:%s" % (job['result']))
        newvfw = self.empty(lvfw, self.vfw.virtualfirewall.new)
        newvfw.gid = self.rgid
        newvfw.id = lvfw.id
        newvfw.nid = int(provider['referenceId'])
        if not self.dryrun:
            self.vfw.virtualfirewall.set(newvfw)

    def create_metaiso(self, vm, provider):
        self.info('Creating metaiso for vm {}'.format(vm.name), 3)
        name = 'vm-{}'.format(vm.id) 
        image = self.ccl.image.get(vm.imageId)
        vmpassword = 'Unknown'
        for account in vm.accounts:
            vmpassword = account.password
        if not self.dryrun:
            volume = provider._create_metadata_iso(name, vmpassword, image.type)
        else:
            volume = MaskClass()
            volume.name = 'something'
            volume.edgehost = 'something'
            volume.edgeport = 'something'
        return volume

    def create_disk(self, disk, vmid, provider):
        self.info('Creating disk {} {}'.format(disk.name, vmid), 3)
        if disk.type == 'B':
            client = provider.getNextEdgeClient('vmstor')
            diskname = 'vm-{0}/bootdisk-vm-{0}'.format(vmid)
            kwargs = {'ovs_connection': provider.ovs_connection,
                      'vpoolguid': client['vpoolguid'],
                      'storagerouterguid': client['storagerouterguid'],
                      'diskname': diskname,
                      'size': disk.sizeMax,
                      'pagecache_ratio': provider.ovs_settings['vpool_data_metadatacache']}
            if not self.dryrun:
                vdiskguid = provider._execute_agent_job('createdisk', role='storagedriver', **kwargs)
                disk.referenceId = provider.getVolumeId(vdiskguid=vdiskguid, edgeclient=client, name=diskname)
                self.ccl.disk.set(disk)
            else:
                disk.referenceId = 'openvstorage+tcp://127.0.0.1:23022/{}@uuuid'.format(diskname)
        else:
            volume = provider.client.create_volume(disk.sizeMax, disk.id)
            disk.referenceId = volume.id
            if not self.dryrun:
                self.ccl.disk.set(disk)

    def get_volume_from_xml(self, xmldom, name):
        devices = xmldom.find('devices')
        for disk in devices.iterfind('disk'):
            source = disk.find('source')
            if source.attrib.get('dev', source.attrib.get('name')) == name:
                return devices, disk
        return None, None
    
    def migrate_vm(self, vm, newspace):
        import libvirt
        self.info('Migrating vm {}'.format(vm.name), 2)
        provider = self.rcb.getProviderByGID(self.rgid).client
        sourcestack = self.source_ccl.stack.get(vm.stackId)
        sourcecon = libvirt.open(sourcestack.apiUrl.replace('ssh', 'tcp'))
        try:
            domain = sourcecon.lookupByUUIDString(vm.referenceId)
        except:
            domain = None
        newvm = self.empty(vm, self.ccl.vmachine.new)
        newvm.cloudspaceId = newspace.id
        newvm.disks = []
        disks = []
        for diskid in vm.disks:
            disk = self.source_ccl.disk.get(diskid)
            newdisk = self.empty(disk, self.ccl.disk.new)
            newdisk.referenceId = None
            newdisk.gid = self.rgid
            if not self.dryrun:
                newdisk.id, _, _ = self.ccl.disk.set(newdisk)
            newvm.disks.append(newdisk.id)
            disks.append((disk, newdisk))
        
        # update imageid
        oldimage = self.source_ccl.image.get(vm.imageId)
        newimage = self.ccl.image.search({'name': oldimage.name})[1]
        newvm.imageId = newimage['id']
        # update sizeid
        oldsize = self.source_ccl.size.get(vm.sizeId)
        newsize = self.ccl.size.search({'memory': oldsize.memory, 'vcpus': oldsize.vcpus})[1]
        newvm.sizeId = newsize['id']
        if not self.dryrun:
            newvm.id, _, _ = self.ccl.vmachine.set(newvm)
        metavolume = self.create_metaiso(newvm, provider)
        if domain:
            sourcexml = domain.XMLDesc()
        else:
            sourcexml = self.source_lcl.libvirtdomain.get('domain_{}'.format(vm.referenceId)) 
        xmldom = ElementTree.fromstring(sourcexml)
        # lets create the disks
        for sourcedisk, disk in disks:
            self.create_disk(disk, newvm.id, provider)
            parsedurl = urlparse.urlparse(sourcedisk.referenceId)
            diskname = parsedurl.path.strip('/').split('@', 1)[0]
            newurl = urlparse.urlparse(disk.referenceId)
            newdiskname = newurl.path.strip('/').split('@', 1)[0]
            _, xmldisk = self.get_volume_from_xml(xmldom, diskname)
            source = xmldisk.find('source')
            source.attrib['name'] = newdiskname
            host = source.find('host')
            host.attrib['name'] = newurl.hostname
            host.attrib['port'] = str(newurl.port)
        # lets update cloudinit aswell
        metaname = 'vm-{0}/cloud-init-vm-{0}'.format(vm.id)
        _, xmldisk = self.get_volume_from_xml(xmldom, metaname)
        source = xmldisk.find('source')
        source.attrib['name'] = metavolume.name
        host = source.find('host')
        host.attrib['name'] = metavolume.edgehost
        host.attrib['port'] = str(metavolume.edgeport)
        # now re migrate copying storage
        newxml = ElementTree.tostring(xmldom)
        excludelist = []
        if sourcestack.gid == self.rgid:
            excludelist.append(sourcestack.id)
        deststack = self.rcb.getBestProvider(self.rgid, excludelist=excludelist)
        newvm.stackId = deststack['id']
        if not self.dryrun:
            self.ccl.vmachine.set(newvm)

        # now re migrate
        if domain:
            # create network
            if not self.dryrun:
                provider._execute_agent_job('createnetwork', id=int(deststack['referenceId']), networkid=newspace.networkId)

            isrunning = domain.info()[0] == libvirt.VIR_DOMAIN_RUNNING
            destcon = libvirt.open(deststack['apiUrl'].replace('ssh', 'tcp'))
            flags = libvirt.VIR_MIGRATE_COMPRESSED | libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_NON_SHARED_DISK | \
                    libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE | libvirt.VIR_MIGRATE_PEER2PEER
            self.info('Running migrate to {}'.format(deststack['name']), 3)
            if not self.dryrun:
                domain.migrate2(destcon, flags=flags, dxml=newxml, dname='vm-{}'.format(newvm.id))
        else:
            # we copy over the data
            for sourcedisk, disk in disks:
                sourceurl = sourcedisk.referenceId.split('@')[0].replace('://', ':')
                desturl = disk.referenceId.split('@')[0].replace('://', ':')
                self.info('Copying disk {} to {}'.format(sourceurl, desturl), 3)
                if not self.dryrun:
                    j.system.platform.qemu_img.convert(
                        sourceurl,
                        'raw',
                        desturl,
                        'raw',
                        createTarget=False
                    )

        vm.status = 'DESTROYED'
        if not self.dryrun:
            self.source_ccl.vmachine.set(vm)
            provider._set_persistent_xml(self.rcb.Dummy(id=vm.referenceId), newxml)
        for sourcedisk, disk in disks:
            sourcedisk.status = 'DESTROYED'
            if not self.dryrun:
                self.source_ccl.disk.set(sourcedisk)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--accounts', help='Comma seperated accountids that require migration', required=True)
    parser.add_argument('-d', '--dry-run', dest='dry', action='store_true', default=False)
    parser.add_argument('-c', '--concurrency', dest='concurrency', type=int, default=1, help='Amount of VMs to migrate at once')
    options = parser.parse_args()
    migrator = Migrator(True, options.dry)
    for accountid in options.accounts.split(','):
        migrator.migrate_account(int(accountid))