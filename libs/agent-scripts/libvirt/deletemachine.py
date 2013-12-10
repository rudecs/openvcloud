from JumpScale import j

descr = """
Libvirt script to delete a virtual machine
"""

name = "deletemachine"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid):
    import libvirt
    from xml.etree import ElementTree

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

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
                if disk.attrib['device'] == 'disk':
                    source = disk.find('source')
                    if source != None:
                        diskfiles.append(source.attrib['dev'])
            return diskfiles


    connection = libvirtconn()
    return connection.delete_machine(machineid)


