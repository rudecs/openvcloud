from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "softrebootmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hamdy.farag@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, xml):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.reboot(machineid, xml)
