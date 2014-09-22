from JumpScale import j
import os

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
    backuppath   = '/mnt/cephfs'
    if not os.path.ismount(backuppath):
        raise "No device mounted on %s" % backuppath
    
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.backup_machine_to_filesystem(machineid, backuppath)
