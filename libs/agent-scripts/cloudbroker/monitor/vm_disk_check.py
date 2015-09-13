from JumpScale import j

descr = """
Checks vmachine disk(s)
"""

organization = 'jumpscale'
name = 'vm_disk_check'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

enable = True
async = True
log = False

def action(vm_id):
    import sys
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList
    from ovs.lib.vmachine import VMachineController

    vmname = 'vm-%s' % vm_id
    vmachine = VMachineList.get_vmachine_by_name(vmname)[0]
    disks = []
    for vdisk in vmachine.vdisks:
        info = vdisk.info.copy()
        info['devicename'] = vdisk.devicename
        disks.append(info)
    return disks
