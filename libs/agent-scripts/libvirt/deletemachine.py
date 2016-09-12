from JumpScale import j

descr = """
Libvirt script to delete a virtual machine
"""

name = "deletemachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []


def action(machineid, machinexml):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.delete_machine(machineid, machinexml)


