from JumpScale import j

descr = """
Libvirt script to create a virtual machine
"""

name = "startmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, xml=None, vmlog_dir=None):
    j.system.fs.createDir(vmlog_dir)
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.create(machineid, xml)
