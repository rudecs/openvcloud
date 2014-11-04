from JumpScale import j

descr = """
Stops a vmachine if it's abusing node's resources, and moves it to slower storage
"""

name = "vm_stop_for_abusive_usage"
category = "cloudbroker"
organization = "cloudscalers"
author = "zains@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"

def action(machineId, nodeId):
    # shutdown the vmachine
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    connection.shutdown(nodeId)

    # move the vmachine to slower storage
    src = j.system.fs.joinPaths('/mnt', 'vmstor', 'vm-%s' % machineId)
    dest = j.system.fs.joinPaths('/mnt', 'vmstor2', 'vm-%s' % machineId)
    j.system.fs.moveDir(src, dest)
    j.system.fs.symlink(dest, j.system.fs.joinPaths('/mnt', 'vmstor'))