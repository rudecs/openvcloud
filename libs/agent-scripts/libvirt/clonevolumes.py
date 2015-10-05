from JumpScale import j

descr = """
Libvirt script to clone volumes
"""

category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'hypervisor'


def action(machineid, name, diskmapping, pmachineip):
    import sys
    import os
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil, lockDomain, unlockDomain
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList
    from ovs.lib.vdisk import PMachineList, VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.lib.vmachine import VMachineController

    connection = LibvirtUtil()
    vmname = connection.get_domain(machineid)['name']
    lockDomain(machineid)
    try:
        pmguid = PMachineList.get_by_ip(pmachineip).guid
        vmachine = VMachineList.get_vmachine_by_name(vmname)[0]
        VMachineController.snapshot(vmachine.guid, 'vm-clone')
        vmachine.invalidate_dynamics(['snapshots'])
        snapshottimestamp = vmachine.snapshots[-1]['timestamp']

        diskpaths = []

        def getVDisk(path):
            for vdisk in vmachine.vdisks:
                filepath = j.system.fs.joinPaths('/mnt/vmstor', vdisk.devicename)
                if filepath == path:
                    return vdisk

        def getSnapshot(vdisk):
            for snap in vdisk.snapshots[::-1]:
                if snap['timestamp'] == snapshottimestamp:
                    return snap

        for diskmap in diskmapping:
            vdisk = getVDisk(diskmap['diskpath'])
            if diskmap['type'] == 'B':
                folder = '%s/base' % name
                diskname = 'image'
            else:
                folder = 'volumes/volume'
                diskname = str(diskmap['cloneId'])

            snapshot = getSnapshot(vdisk)
            newdisk = VDiskController.clone(vdisk.guid, snapshot['guid'], diskname, pmguid, folder)
            filepath = j.system.fs.joinPaths('/mnt/vmstor', newdisk['backingdevice'].lstrip('/'))
            diskpaths.append(filepath)

        return diskpaths
    finally:
        unlockDomain(machineid)


