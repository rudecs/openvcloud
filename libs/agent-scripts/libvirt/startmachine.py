from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "startmachine"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid, xml = None):
    import libvirt

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

        def create(self, id, xml):
            domain = self._get_domain(id)
            if not domain and xml:
                domain = self.connection.defineXML(xml)
            return domain.create() == 0

        def _get_domain(self, id):
            try:
                domain = self.connection.lookupByUUIDString(id)
            except libvirt.libvirtError, e:
                if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                    return None
            return domain


    connection = libvirtconn()
    return connection.create(machineid, xml)



