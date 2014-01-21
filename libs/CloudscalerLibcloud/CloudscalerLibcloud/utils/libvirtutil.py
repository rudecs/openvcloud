import libvirt
from xml.etree import ElementTree
from jinja2 import Environment, PackageLoader
import os

class LibvirtUtil(object):
    def __init__(self):
        self.connection = libvirt.open()
        self.readonly = libvirt.openReadOnly()
        self.basepath = '/mnt/vmstor'
        self.env = Environment(loader=PackageLoader('CloudscalerLibcloud', 'templates'))


    def _get_domain(self, id):
        try:
            domain = self.connection.lookupByUUIDString(id)
        except libvirt.libvirtError, e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                return None
        return domain

    def create(self, id, xml):
        domain = self._get_domain(id)
        if not domain and xml:
            domain = self.connection.defineXML(xml)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_RUNNING:
            return True
        return domain.create() == 0

    def shutdown(self, id):
        domain = self._get_domain(id)
        if domain.state(0)[0] in [libvirt.VIR_DOMAIN_SHUTDOWN, libvirt.VIR_DOMAIN_SHUTOFF, libvirt.VIR_DOMAIN_CRASHED]:
            return True
        return domain.shutdown() == 0

    def suspend(self, id):
        domain = self._get_domain(id)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_PAUSED:
            return True
        return domain.suspend() == 0

    def resume(self, id):
        domain = self._get_domain(id)
        if domain.state(0)[0] == libvirt.VIR_DOMAIN_RUNNING:
            return True
        return domain.resume() == 0

    def delete_machine(self, machineid):
        domain = self.connection.lookupByUUIDString(machineid)
        diskfiles = self._get_domain_disk_file_names(domain)
        if domain.state(0)[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            domain.destroy()

        for diskfile in diskfiles:
            vol = self.connection.storageVolLookupByPath(diskfile)
            diskpool = vol.storagePoolLookupByVolume()
            vol.delete(0)
            if diskpool.numOfVolumes() == 0:
                poolpath = os.path.join(self.basepath, diskpool.name())
                diskpool.destroy()
                if os.path.exists(poolpath):
                    os.removedirs(poolpath)
        domain.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def _get_domain_disk_file_names(self, dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        else:
            xml = ElementTree.fromstring(dom.XMLDesc(0))
            disks = xml.findall('devices/disk')
            diskfiles = list()
        for disk in disks:
            if disk.attrib['device'] == 'disk' or disk.attrib['device'] == 'cdrom':
                source = disk.find('source')
                if source != None:
                    if disk.attrib['device'] == 'disk':
                        diskfiles.append(source.attrib['dev'])
                    if disk.attrib['device'] == 'cdrom':
                        diskfiles.append(source.attrib['file'])
        return diskfiles

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
            totalmax += maxmem/1000
            if machinestate == libvirt.VIR_DOMAIN_RUNNING:
                totalrunningmax += maxmem/1000
        return (hostmem, totalmax, totalrunningmax)



    def check_machine(self, machinexml):
        xml = ElementTree.fromstring(machinexml)
        memory = int(xml.find('memory').text)
        hostmem, totalmax, totalrunningmax = self.memory_usage()
        if (totalrunningmax + memory) > (hostmem - 1024):
            return False
        return True

    def snapshot(self, id, xml, snapshottype):
        domain = self._get_domain(id)
        flags = 0 if snapshottype == 'internal' else libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY
        snap = domain.snapshotCreateXML(xml, flags)
        return {'name':snap.getName(), 'xml':snap.getXMLDesc()}

    def listSnapshots(self, id):
        domain = self._get_domain(id)
        results = list()
        for snapshot in domain.listAllSnapshots():
            xml = ElementTree.fromstring(snapshot.getXMLDesc())
            snap = {'name': xml.find('name').text,
                    'epoch': int(xml.find('creationTime').text) }
            results.append(snap)
        return results

    def deleteVolume(self, path):
        vol = self.connection.storageVolLookupByPath(path)
        return vol.delete(0)

    def getSnapshot(self, domain, name):
        domain = self._get_domain(domain)
        snap = domain.snapshotLookupByName('name')
        return {'name': snap.getName(), 'epoch': snap.getXMLDesc()}

    def deleteSnapshot(self, id, name):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        return snapshot.delete(0) == 0

    def rollbackSnapshot(self, id, name):
        domain = self._get_domain(id)
        snapshot = domain.snapshotLookupByName(name, 0)
        return domain.revertToSnapshot(snapshot, libvirt.VIR_DOMAIN_SNAPSHOT_REVERT_FORCE) == 0

    def create_disk(self, diskxml, poolname):
        pool = self._get_pool(poolname)
        pool.createXML(diskxml, 0)
        return True


    def _get_pool(self, poolname):
        storagepool = self.connection.storagePoolLookupByName(poolname)
        return storagepool

    def check_storagepool(self, poolname):
        if poolname not in self.connection.listStoragePools():
            poolpath = os.path.join(self.basepath, poolname)
            if not os.path.exists(poolpath):
                os.makedirs(poolpath)
            pool = self.env.get_template('pool.xml').render(poolname=poolname, basepath=self.basepath)
            self.connection.storagePoolCreateXML(pool, 0)
        return True
            
    def create_machine(self, machinexml):
        domain = self.connection.defineXML(machinexml)
        domain.create()
        return self._to_node(domain)

    def _to_node(self, domain):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time}
        return {'id': domain.UUIDString(), 'name': domain.name(), 'state':state, 'extra': extra, 'XMLDesc': domain.XMLDesc(0)}

    def get_domain(self, uuid):
        domain = self.connection.lookupByUUIDString(uuid)
        return self._to_node(domain)

    def list_domains(self):
        nodes = []
        for x in self.connection.listAllDomains(0):
            nodes.append(self._to_node(x))
        return nodes
