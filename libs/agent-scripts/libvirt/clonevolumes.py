from JumpScale import j

descr = """
Libvirt script to clone volumes
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'hypervisor'


def action(machineid, name, diskmapping):
    import time
    from CloudscalerLibcloud import openvstorage
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil, lockDomain, unlockDomain
    from ovs.lib.vdisk import VDiskController

    lockDomain(machineid)
    try:
        storagerouter = openvstorage.getLocalStorageRouter()
        diskpaths = []
        timestamp = str(int(time.time()))

        def getSnapshot(vdisk):

            meta = {'label': 'for clone %s' % name,
                    'is_consistent': False,
                    'is_sticky': True,
                    'is_automatic': False,
                    'timestamp': timestamp}
            return VDiskController.create_snapshot(vdisk.guid, meta)

        for diskmap in diskmapping:
            vdisk = openvstorage.getVDisk(diskmap['diskpath'])
            if diskmap['type'] == 'B':
                diskname = '%s/base-image' % name
            else:
                diskname = 'volumes/volume-%s' % diskmap['cloneId']

            snapshot = getSnapshot(vdisk)
            newdisk = VDiskController.clone(vdisk.guid, diskname, snapshot, storagerouter.guid)
            filepath = openvstorage.getUrlPath(newdisk['backingdevice'].lstrip('/'))
            diskpaths.append(filepath)

        return diskpaths
    finally:
        unlockDomain(machineid)


