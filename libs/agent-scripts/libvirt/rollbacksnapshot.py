from JumpScale import j

descr = """
Rollback a snapshot on a machine
"""

name = "rollbacksnapshot"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid, name):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.rollbackSnapshot(machineid, name)
