from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.reboot(machineid)



