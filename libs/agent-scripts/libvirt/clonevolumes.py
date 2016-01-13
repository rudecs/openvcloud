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
    import time
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil, lockDomain, unlockDomain
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vmachinelist import VMachineList
    from ovs.lib.vdisk import PMachineList, VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    lockDomain(machineid)
    try:
        pmguid = PMachineList.get_by_ip(pmachineip).guid
        pool = VPoolList.get_vpool_by_name('vmstor')
        diskpaths = []
        timestamp = str(int(time.time()))

        def getVDisk(path):
            diskpath = path.replace('/mnt/vmstor/', '')
            return VDiskList.get_by_devicename_and_vpool(diskpath, pool)

        def getSnapshot(vdisk):

            meta = {'label': 'for clone %s' % name,
                    'is_consistent': False,
                    'is_sticky': True,
                    'is_automatic': False,
                    'timestamp': timestamp}
            return VDiskController.create_snapshot(vdisk.guid, meta)

        for diskmap in diskmapping:
            vdisk = getVDisk(diskmap['diskpath'])
            if diskmap['type'] == 'B':
                folder = '%s/base' % name
                diskname = 'image'
            else:
                folder = 'volumes/volume'
                diskname = str(diskmap['cloneId'])

            snapshot = getSnapshot(vdisk)
            newdisk = VDiskController.clone(vdisk.guid, snapshot, diskname, pmguid, folder)
            filepath = j.system.fs.joinPaths('/mnt/vmstor', newdisk['backingdevice'].lstrip('/'))
            diskpaths.append(filepath)

        return diskpaths
    finally:
        unlockDomain(machineid)


