import libvirt
from xml.etree import ElementTree

class LibvirtUtil(object):
    def __init__(self):
        self.connection = libvirt.open()

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
            vol.delete(0)
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

    def snapshot(self, id, xml, snapshottype):
        domain = self._get_domain(id)
        flags = 0 if snapshottype == 'internal' else libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY
        return domain.snapshotCreateXML(xml, flags).getName()

    def listSnapshots(self, id):
        domain = self._get_domain(id)
        results = list()
        for snapshot in domain.listAllSnapshots():
            xml = ElementTree.fromstring(snapshot.getXMLDesc())
            snap = {'name': xml.find('name').text,
                    'epoch': int(xml.find('creationTime').text) }
            results.append(snap)

        return results

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

    def _get_pool(self, poolname):
        storagepool = self.connection.storagePoolLookupByName(poolname)
        return storagepool


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
