from JumpScale import j

descr = """
Libvirt script to delete a virtual machine
"""

name = "deletemachine"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.backup_machine_cephfs(machineid)


