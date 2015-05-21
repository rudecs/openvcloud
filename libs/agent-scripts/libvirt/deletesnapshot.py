from JumpScale import j

descr = """
Delete snapshot of machine
"""

name = "deletesnapshot"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid, name):
    import sys
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList
    from ovs.lib.vdisk import VDiskController

    connection = LibvirtUtil()
    vmname = connection.get_domain(machineid)['name']
    vmachine = VMachineList.get_vmachine_by_name(vmname)[0]
    for snap in vmachine.snapshots:
        if snap['label'] == name:
            for diskguid, snapid in snap['snapshots'].iteritems():
                VDiskController.delete_snapshot(diskguid, snapid)
    return True

