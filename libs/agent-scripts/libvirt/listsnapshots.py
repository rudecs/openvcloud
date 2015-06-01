from JumpScale import j

descr = """
List snapshot of specific machine
"""

name = "listsnapshots"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid):
    import sys
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList

    connection = LibvirtUtil()
    vmname = connection.get_domain(machineid)['name']
    vmachines = VMachineList.get_vmachine_by_name(vmname) or []
    snapshots = list()
    for vmachine in vmachines:
        for snap in vmachine.snapshots:
            if not snap['is_automatic']:
                snapshots.append({'name': snap['label'], 'epoch': int(snap['timestamp'])})
    return snapshots
