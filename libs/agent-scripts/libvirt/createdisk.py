from JumpScale import j

descr = """
Libvirt script to create a disk
"""

name = "createdisk"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]
async = True


def action(diskxml, poolname):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    if not connection.check_disk(diskxml):
    	return -1
    connection.check_storagepool(poolname)
    return connection.create_disk(diskxml, poolname)


