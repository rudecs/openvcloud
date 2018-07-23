from JumpScale import j

descr = """
Libvirt script to create a machine
"""

name = "createmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'hypervisor'


def action(machinexml, vmlog_dir=None):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    j.system.fs.createDir(vmlog_dir)
    connection = LibvirtUtil()
    if not connection.check_machine(machinexml):
        return -1
    return connection.create_machine(machinexml)
