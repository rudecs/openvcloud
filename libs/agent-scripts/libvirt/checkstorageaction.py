from JumpScale import j

descr = """
Check if there is a storage action running
"""

name = "checkstorageaction"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.isCurrentStorageAction(machineid)


