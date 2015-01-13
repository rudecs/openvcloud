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
roles = []
async = True
queue = "hypervisor"


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.soft_reboot_node(machineid, soft=True)



