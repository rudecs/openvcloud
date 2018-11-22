import libvirt
from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader
import os
import time
import shutil
import urlparse
from multiprocessing import cpu_count
from CloudscalerLibcloud.utils.qcow2 import Qcow2
from JumpScale import j
from JumpScale.lib.ovsnetconfig.VXNet import netclasses
from CloudscalerLibcloud.utils.gridconfig import GridConfig


LOCKCREATED = 1
LOCKREMOVED = 2
NOLOCK = 3
LOCKEXIST = 4

CPU_COUNT = cpu_count()
if CPU_COUNT <= 16:
    RESERVED_CPUS = 1
elif 16 < CPU_COUNT < 32:
    RESERVED_CPUS = 2
else:
    RESERVED_CPUS = 4


class TimeoutError(Exception):
    pass


def _getLockFile(domainid):
    LOCKPATH = '%s/domain_locks' % j.dirs.varDir
    if not j.system.fs.exists(LOCKPATH):
        j.system.fs.createDir(LOCKPATH)
    lockfile = '%s/%s.lock' % (LOCKPATH, domainid)
    return lockfile


def lockDomain(domainid):
    if isLocked(domainid):
        return LOCKEXIST
    j.system.fs.writeFile(_getLockFile(domainid), str(time.time()))
    return LOCKCREATED


def unlockDomain(domainid):
    if not isLocked(domainid):
        return NOLOCK
    j.system.fs.remove(_getLockFile(domainid))
    return LOCKREMOVED


def isLocked(domainid):
    if j.system.fs.exists(_getLockFile(domainid)):
        return True
    else:
        return False


def lockedAction(func):
    def wrapper(s, id, *args, **kwargs):
        lock = lockDomain(id)
        if lock != LOCKCREATED:
            raise RuntimeError("Can not perform action on locked machine")
        try:
            return func(s, id, *args, **kwargs)
        finally:
            unlockDomain(id)

    return wrapper


class LibvirtUtil(object):

    def __init__(self):
        self.connection = libvirt.open()
        self.readonly = libvirt.openReadOnly()
        self.basepath = '/mnt/vmstor'
        self.templatepath = '/mnt/vmstor/templates'
        self.env = Environment(loader=PackageLoader(
            'CloudscalerLibcloud', 'templates'))
        self.config = GridConfig()

    def _get_domain(self, id):
        try:
            domain = self.connection.lookupByUUIDString(id)
        except libvirt.libvirtError, e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return None
        return domain

    def close(self):
        self.connection.close()
        self.readonly.close()

    def get_domain_obj(self, id):
        return self._get_domain(id)

    def modXML(self, xml):
        root = ElementTree.fromstring(xml)
        vcpu = root.find("vcpu")
        vcpu.set("cpuset", "{startcpu}-{cpulimit}".format(startcpu=RESERVED_CPUS, cpulimit=CPU_COUNT - 1))
        xml = ElementTree.tostring(root)
        return xml

    def defineXML(self, xml):
        xml = self.modXML(xml)
        return self.connection.defineXML(xml)

    def create(self, id, xml):
        if isLocked(id):
            raise Exception("Can't start a locked machine")
        domain = self._get_domain(id)
        if domain:
            state = domain.state()[0]
            if state == libvirt.VIR_DOMAIN_RUNNING:
                return domain.XMLDesc()
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                domain.resume()
        else:
            xml = self.modXML(xml)
            domain = self.connection.createXML(xml)
        return domain.XMLDesc()

    def shutdown(self, id, force=False):
        if isLocked(id):
            raise Exception("Can't stop a locked machine")
        domain = self._get_domain(id)
        if domain:
            isPersistent = domain.isPersistent()
            networkid = self._get_domain_networkid(domain)
            bridges = list(self._get_domain_bridges(domain))
            if domain.state()[0] not in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
                if force:
                    domain.destroy()
                else:
                    if not domain.shutdown() == 0:
                        return False
                    try:
                        self.waitForAction(id, timeout=30000, events=[libvirt.VIR_DOMAIN_EVENT_STOPPED])
                    except TimeoutError, e:
                        j.errorconditionhandler.processPythonExceptionObject(e)
                        domain.destroy()
            if isPersistent:
                domain.undefine()
            if networkid or bridges:
                self.cleanupNetwork(networkid, bridges)
        return True

    def waitForAction(self, domid, timeout=None, events=None):
        libvirt.virEventRegisterDefaultImpl()
        rocon = libvirt.openReadOnly()
        run = {'state': True, 'timeout': False}

        def timecb(timerid, opaque):
            run['state'] = False
            run['timeout'] = True

        def callback(con, domain, event, detail, opaque):
            if domain.UUIDString() == domid:
                if events is not None and event in events:
                    run['state'] = False
                    return True

        if timeout:
            libvirt.virEventAddTimeout(timeout, timecb, None)
        rocon.domainEventRegisterAny(None,
                                     libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                     callback,
                                     rocon)
        while run['state']:
            libvirt.virEventRunDefaultImpl()

        if run['timeout']:
            raise TimeoutError("Failed to wait for state")

    def reboot(self, id, xml):
        if isLocked(id):
            raise Exception("Can't reboot a locked machine")
        domain = self._get_domain(id)
        if domain:
            if domain.state()[0] in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
                domain.create()
            else:
                domain.reboot()
        else:
            self.create(id, xml)
        return True

    def suspend(self, id):
        if isLocked(id):
            raise Exception("Can't suspend a locked machine")
        domain = self._get_domain(id)
        if domain.state()[0] == libvirt.VIR_DOMAIN_PAUSED:
            return True
        return domain.suspend() == 0

    def resume(self, id):
        if isLocked(id):
            raise Exception("Can't resume a locked machine")
        domain = self._get_domain(id)
        if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
            return True
        return domain.resume() == 0

    def delete_machine(self, machineid, machinexml):
        if isLocked(id):
            raise Exception("Can't delete a locked machine")
        try:
            domain = self.connection.lookupByUUIDString(machineid)
            xml = ElementTree.fromstring(domain.XMLDesc())
        except:
            domain = None
            xml = ElementTree.fromstring(machinexml)
        networkid = self._get_domain_networkid(xml)
        bridges = self._get_domain_bridges(xml)
        if domain:
            if domain.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
                domain.destroy()
            try:
                domain.undefine()
            except:
                pass  # none persistant vms dont need to be undefined
        if networkid or bridges:
            self.cleanupNetwork(networkid, bridges)
        name = xml.find('name').text
        poolpath = os.path.join(self.basepath, name)
        return True

    def get_domain_disks(self, dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        elif isinstance(dom, basestring):
            xml = ElementTree.fromstring(dom)
        else:
            xml = ElementTree.fromstring(dom.XMLDesc(0))
        disks = xml.findall('devices/disk')
        for disk in disks:
            if disk.attrib['device'] in ('disk', 'cdrom'):
                yield disk

    def get_domain_disk(self, referenceId, domaindisks):
        url = urlparse.urlparse(referenceId)
        name = url.path.split('@')[0].strip('/').split(':')[0]
        for disk in domaindisks:
            source = disk.find('source')
            if source is not None:
                if source.attrib.get('name', '').strip('/') == name:
                    target = disk.find('target')
                    return target.attrib['dev']

    def get_domain_nics(self, dom):
        xml = self._get_xml_dom(dom)
        for target in xml.findall('devices/interface/target'):
            yield target.attrib['dev']

    def get_domain_nics_info(self, dom):
        xml = self._get_xml_dom(dom)
        for interface in xml.findall('devices/interface'):
            nic = {}
            nic['mac'] = interface.find('mac').attrib['address']
            nic['name'] = interface.find('target').attrib['dev']
            source = interface.find('source')
            nic['bridge'] = source.attrib['bridge'] if source.attrib.get('bridge') else source.attrib['network']
            yield nic


    def _get_xml_dom(self, dom):
        if isinstance(dom, ElementTree.Element):
            return dom
        elif isinstance(dom, basestring):
            return ElementTree.fromstring(dom)
        else:
            return ElementTree.fromstring(dom.XMLDesc(0))

    def _get_domain_disk_file_names(self, dom):
        diskfiles = list()
        for disk in self.get_domain_disks(dom):
            source = disk.find('source')
            if source is not None:
                if source.attrib.get('protocol') == 'openvstorage':
                    diskfiles.append(os.path.join(self.basepath, source.attrib['name'] + '.raw'))
                else:
                    if 'dev' in source.attrib:
                        diskfiles.append(source.attrib['dev'])
                    if 'file' in source.attrib:
                        diskfiles.append(source.attrib['file'])
        return diskfiles

    def _get_domain_bridges(self, dom):
        xml = self._get_xml_dom(dom)
        interfaces = xml.findall('devices/interface/source')
        for interface in interfaces:
            for network_key in ['bridge', 'network']:
                if network_key in interface.attrib:
                    yield interface.attrib[network_key]

    def _get_domain_networkid(self, dom):
        for bridge in self._get_domain_bridges(dom):
            if bridge.startswith('space_'):
                networkid = bridge.partition('_')[-1]
                return int(networkid, 16)
        return None

    def check_disk(self, diskxml):
        return True

    def memory_usage(self):
        ids = self.readonly.listDomainsID()
        hostmem = self.readonly.getInfo()[1]
        totalmax = 0
        totalrunningmax = 0
        for id in ids:
            dom = self.readonly.lookupByID(id)
            machinestate, maxmem, mem = dom.info()[0:3]
            totalmax += mem / 1024
            if machinestate == libvirt.VIR_DOMAIN_RUNNING:
                totalrunningmax += maxmem / 1024
        return (hostmem, totalmax, totalrunningmax)

    def check_machine(self, machinexml, reserved_mem=None):
        if reserved_mem is None:
            reserved_mem = self.config.get("reserved_mem")
        xml = ElementTree.fromstring(machinexml)
        memory = int(xml.find('currentMemory').text)
        hostmem, totalmax, totalrunningmax = self.memory_usage()
        if (totalrunningmax + memory) > (hostmem - reserved_mem):
            return False
        return True

    def snapshot(self, id, xml, snapshottype):
        if isLocked(id):
            raise Exception("Can't snapshot a locked machine")
        domain = self._get_domain(id)
        flags = 0 if snapshottype == 'internal' else libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY
        snap = domain.snapshotCreateXML(xml, flags)
        return {'name': snap.getName(), 'xml': snap.getXMLDesc()}

    def listSnapshots(self, id):
        domain = self._get_domain(id)
        results = list()
        for snapshot in domain.listAllSnapshots():
            xml = ElementTree.fromstring(snapshot.getXMLDesc())
            snap = {'name': xml.find('name').text,
                    'epoch': int(xml.find('creationTime').text)}
            results.append(snap)
        return results

    def deleteVolume(self, path):
        vol = self.connection.storageVolLookupByPath(path)
        return vol.delete(0)

    def getSnapshot(self, domain, name):
        domain = self._get_domain(domain)
        snap = domain.snapshotLookupByName('name')
        return {'name': snap.getName(), 'epoch': snap.getXMLDesc()}

    def _isRootVolume(self, domain, file):
        diskfiles = self._get_domain_disk_file_names(domain)
        if file in diskfiles:
            return True
        return False

    def _renameSnapshot(self, id, name, newname):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        xml = snapshot.getXMLDesc()
        newxml = xml.replace('<name>%s</name>' %
                             name, '<name>%s</name>' % newname)
        domain.snapshotCreateXML(
            newxml, (libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_REDEFINE or libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY))
        snapshot.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def deleteSnapshot(self, id, name):
        if isLocked(id):
            raise Exception("Can't delete a snapshot from a locked machine")
        newname = '%s_%s' % (name, 'DELETING')
        self._renameSnapshot(id, name, newname)
        name = newname
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotfiles = self._getSnapshotDisks(id, name)
        volumes = []
        todelete = []
        for snapshotfile in snapshotfiles:
            is_root_volume = self._isRootVolume(
                domain, snapshotfile['file'].path)
            if not is_root_volume:
                print 'Blockcommit from %s to %s' % (snapshotfile['file'].path, snapshotfile['file'].backing_file_path)
                domain.blockCommit(snapshotfile['name'], snapshotfile[
                                   'file'].backing_file_path, snapshotfile['file'].path)
                todelete.append(snapshotfile['file'].path)
                volumes.append(snapshotfile['name'])
            else:
                # we can't use blockcommit on topsnapshots
                new_base = Qcow2(
                    snapshotfile['file'].backing_file_path).backing_file_path
                todelete.append(snapshotfile['file'].backing_file_path)
                if not new_base:
                    continue
                print 'Blockrebase from %s' % new_base
                flags = libvirt.VIR_DOMAIN_BLOCK_REBASE_COPY | libvirt.VIR_DOMAIN_BLOCK_REBASE_REUSE_EXT | libvirt.VIR_DOMAIN_BLOCK_REBASE_SHALLOW
                domain.blockRebase(snapshotfile['name'], new_base, flags)
                volumes.append(snapshotfile['name'])

        while not self._block_job_domain_info(domain, volumes):
            time.sleep(0.5)

        # we can undefine the snapshot
        snapshot.delete(flags=libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        for disk in todelete:
            if os.path.exists(disk):
                os.remove(disk)
        return True

    def _block_job_domain_info(self, domain, paths):
        for path in paths:
            done = self._block_job_info(domain, path)
            if not done:
                return False
        return True

    def _block_job_info(self, domain, path):
        status = domain.blockJobInfo(path, 0)
        print status
        try:
            cur = status.get('cur', 0)
            end = status.get('end', 0)
            if cur != 0 and end != 0:
                per = int((cur / float(end)) * 100)
                j.logger.log('Copy progress %s' % per, 1, 'progress',
                             tags="id:%s per:%s" % (domain.UUIDString(), per))
            if cur == end:
                return True
        except Exception:
            return True
        else:
            return False

    def rollbackSnapshot(self, id, name, deletechildren=True):
        if isLocked(id):
            raise Exception("Can't rollback a locked machine")
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotdomainxml = ElementTree.fromstring(snapshot.getXMLDesc(0))
        domainxml = snapshotdomainxml.find('domain')
        newxml = ElementTree.tostring(domainxml)
        self.defineXML(newxml)
        if deletechildren:
            children = snapshot.listAllChildren(1)
            for child in children:
                snapshotfiles = self._getSnapshotDisks(id, child.getName())
                for snapshotfile in snapshotfiles:
                    os.remove(snapshotfile['file'].path)
                child.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
            snapshotfiles = self._getSnapshotDisks(id, name)
            for snapshotfile in snapshotfiles:
                os.remove(snapshotfile['file'].path)
            snapshot.delete(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def getProgressLogger(self, id, tmpl='%s'):
        def wrapper(per):
            j.logger.log(tmpl % per, 1, 'progress', tags="id:%s per:%s" % (id, per))
        return wrapper

    @lockedAction
    def _clone(self, id, filename, clonefrom):
        domain = self.connection.lookupByUUIDString(id)
        domainconfig = domain.XMLDesc()
        destination_path = os.path.join(self.templatepath, filename)
        if domain.state()[0] in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED, libvirt.VIR_DOMAIN_PAUSED] or not self._isRootVolume(domain, clonefrom):
            size = int(j.system.platform.qemu_img.info(clonefrom, unit='')['virtual size'])
            fd = os.open(destination_path, os.O_RDWR | os.O_CREAT)
            try:
                os.ftruncate(fd, size)
            finally:
                os.close(fd)
            j.system.platform.qemu_img.convert(clonefrom, 'raw', destination_path, 'raw', createTarget=False)
        else:
            domain.undefine()
            try:
                flags = libvirt.VIR_DOMAIN_BLOCK_REBASE_COPY | libvirt.VIR_DOMAIN_BLOCK_REBASE_COPY_RAW
                domain.blockRebase(clonefrom, destination_path, 0, flags)
                rebasedone = False
                while not rebasedone:
                    rebasedone = self._block_job_info(domain, clonefrom)
            finally:
                self.defineXML(domainconfig)
        return destination_path

    def exportToTemplate(self, id, name, clonefrom, filename):
        if isLocked(id):
            raise Exception("Can't export a locked machine")
        domain = self.connection.lookupByUUIDString(id)
        if not clonefrom:
            domaindisks = self._get_domain_disk_file_names(domain)
            if len(domaindisks) > 0:
                clonefrom = domaindisks[0]
            else:
                raise Exception('Node image found for this machine')
        else:
            snapshotfiles = self._getSnapshotDisks(id, name)
            # we just take the first one at this moment
            if len(snapshotfiles) > 0:
                clonefrom = snapshotfiles[0]['file'].backing_file_path
            else:
                raise Exception('No snapshot found')
        destination_path = self._clone(id, filename, clonefrom)
        return destination_path

    def create_disk(self, diskxml, poolname):
        pool = self._get_pool(poolname)
        return pool.createXML(diskxml, 0)

    def _getSnapshotDisks(self, id, name):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        snapshotxml = ElementTree.fromstring(snapshot.getXMLDesc(0))
        snapshotfiles = []
        disks = snapshotxml.findall('disks/disk')
        for disk in disks:
            source = disk.find('source')
            if source is not None and disk.attrib['snapshot'] == 'external':
                snapshotfiles.append(
                    {'name': disk.attrib['name'], 'file': Qcow2(source.attrib['file'])})
        return snapshotfiles

    def _get_pool(self, poolname):
        storagepool = self.connection.storagePoolLookupByName(poolname)
        return storagepool

    def check_storagepool(self, poolname):
        if poolname not in self.connection.listStoragePools():
            poolpath = os.path.join(self.basepath, poolname)
            if not os.path.exists(poolpath):
                os.makedirs(poolpath)
                cmd = 'chattr +C %s ' % poolpath
                j.system.process.execute(
                    cmd, dieOnNonZeroExitCode=False, outputToStdout=False, useShell=False, ignoreErrorOutput=False)
            pool = self.env.get_template('pool.xml').render(
                poolname=poolname, basepath=self.basepath)
            self.connection.storagePoolCreateXML(pool, 0)
        return True

    def create_machine(self, machinexml):
        xml = self.modXML(machinexml)
        domain = self.connection.createXML(xml)
        return self._to_node(domain)

    def _to_node(self, domain):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        locked = isLocked(domain.UUIDString())
        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(
        ), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time, 'locked': locked}
        return {'id': domain.UUIDString(), 'name': domain.name(), 'state': state, 'extra': extra, 'XMLDesc': domain.XMLDesc(0)}

    def _to_node_list(self, domain):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(
        ), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time}
        return {'id': domain.UUIDString(), 'name': domain.name(), 'state': state, 'extra': extra}

    def get_domain(self, uuid):
        try:
            domain = self.connection.lookupByUUIDString(uuid)
        except:
            return None
        return self._to_node(domain)

    def list_domains(self):
        nodes = []
        for x in self.connection.listAllDomains(0):
            nodes.append(self._to_node_list(x))
        return nodes

    def _getPool(self, domain):
        # poolname is by definition the machine name
        return self.readonly.storagePoolLookupByName(domain.name())

    def _getTemplatePool(self, templatepoolname=None):
        if not templatepoolname:
            templatepoolname = 'VMStor'
        return self.readonly.storagePoolLookupByName(templatepoolname)

    def createNetwork(self, networkname, bridge):
        networkxml = self.env.get_template('network.xml').render(
            networkname=networkname, bridge=bridge)
        network = self.connection.networkDefineXML(networkxml)
        network.create()
        network.setAutostart(True)

    def checkNetwork(self, networkname):
        return networkname in self.connection.listNetworks()

    def cleanupNetwork(self, networkid, bridges):
        def destroyNetwork(name):
            try:
                network = self.connection.networkLookupByName(networkname)
                try:
                    network.destroy()
                except:
                    pass
                try:
                    network.undefine()
                except:
                    pass
            except:
                # network does not exists
                pass

        if networkid and j.system.ovsnetconfig.cleanupIfUnused(networkid):
            networkname = netclasses.VXBridge(networkid).name
            destroyNetwork(networkname)

        for bridge in bridges:
            if not bridge.startswith('ext-'):
                continue
            if j.system.ovsnetconfig.cleanupIfUnusedVlanBridge(bridge):
                destroyNetwork(bridge)

    def createVMStorSnapshot(self, name):
        vmstor_snapshot_path = j.system.fs.joinPaths(
            self.basepath, 'snapshots')
        if not j.system.fs.exists(vmstor_snapshot_path):
            j.system.btrfs.subvolumeCreate(self.basepath, 'snapshots')
        vmstorsnapshotpath = j.system.fs.joinPaths(vmstor_snapshot_path, name)
        j.system.btrfs.snapshotReadOnlyCreate(
            self.basepath, vmstorsnapshotpath)
        return True

    def deleteVMStorSnapshot(self, name):
        vmstor_snapshot_path = j.system.fs.joinPaths(
            self.basepath, 'snapshots')
        j.system.btrfs.subvolumeDelete(vmstor_snapshot_path, name)
        return True

    def listVMStorSnapshots(self):
        vmstor_snapshot_path = j.system.fs.joinPaths(
            self.basepath, 'snapshots')
        return j.system.btrfs.subvolumeList(vmstor_snapshot_path)

    def reset(self, id, xml):
        if isLocked(id):
            raise Exception("Can't reboot a locked machine")
        domain = self._get_domain(id)
        if domain:
            if domain.state()[0] in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
                domain.create()
            else:
                domain.reset()
        else:
            self.create(id, xml)
