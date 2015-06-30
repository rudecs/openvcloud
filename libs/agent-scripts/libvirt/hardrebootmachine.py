from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "hardrebootmachine"
category = "libvirt"
organization = "cloudscalers"
author = "hamdy.farag@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.reset(machineid, soft=False)
