from JumpScale import j

descr = """
Libvirt script to suspend a virtual machine
"""

name = "pausemachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, xml=None):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.suspend(machineid)


