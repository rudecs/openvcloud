from JumpScale import j

descr = """
Script to assure the Libvirt network and the corresponding vxLan exists
"""

name = "createnetwork"
category = "libvirt"
organization = "vscalers"
author = "vscalers.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(networkid):
    networkname = 'default_%s' % networkid
    
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    
    return networkname



