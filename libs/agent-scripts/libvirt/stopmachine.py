from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "stopmachine"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid):
    import libvirt

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

        def shutdown(self, id):
            domain = self._get_domain(id)
            return domain.shutdown() == 0

        def _get_domain(self, id):
            try:
                domain = self.connection.lookupByUUIDString(id)
            except libvirt.libvirtError, e:
                if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                    return None
            return domain


    connection = libvirtconn()
    return connection.shutdown(machineid)



