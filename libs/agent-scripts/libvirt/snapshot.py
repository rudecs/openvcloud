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


def action(machineid, name, snapshottype):
    import sys
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList
    from ovs.lib.vmachine import VMachineController

    connection = LibvirtUtil()
    vmname = connection.get_domain(machineid)['name']
    vmachine = VMachineList.get_vmachine_by_name(vmname)[0]
    VMachineController.snapshot(vmachine.guid, name)
    return {'name': name}
