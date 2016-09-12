from JumpScale import j

descr = """
Libvirt script to ge the domain
"""

name = "getmachine"
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
    return connection.get_domain(machineid)



