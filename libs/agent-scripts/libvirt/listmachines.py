from JumpScale import j

descr = """
Libvirt script to list machines
"""

name = "listmachines"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action():
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.list_domains()



