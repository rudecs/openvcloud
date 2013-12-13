from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "createdisk"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(diskxml, poolname):
    import libvirt

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

        def create_disk(self, diskxml, poolname):
            pool = self._get_pool(poolname)
            pool.createXML(diskxml, 0)

        def _get_pool(self, poolname):
            storagepool = self.connection.storagePoolLookupByName(poolname)
            return storagepool

    connection = libvirtconn()
    return connection.create_disk(diskxml, poolname)


