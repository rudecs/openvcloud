from JumpScale import j

descr = """
Libvirt script to copy (TGZ) a virtual machine to Ceph Filesystem
"""

name = "cloudbroker_backup_cephfs"
category = "libvirt"
organization = "cloudscalers"
author = "jan@mothership1.com"
license = "bsd"
version = "1.0"
roles = []


def action(machineid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.backup_machine_cephfs(machineid)
