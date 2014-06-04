from JumpScale import j

descr = """
Make snapshot of a machine
"""

name = "snapshot"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid, xml, snapshottype):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.snapshot(machineid, xml, snapshottype)
