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

def action(diskpaths):
    import sys
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    pool = VPoolList.get_vpool_by_name('vmstor')
    disks = []
    for diskpath in diskpaths:
        diskpath = diskpath.replace('/mnt/vmstor/', '')
        disk = VDiskList.get_by_devicename_and_vpool(diskpath, pool)
        info = disk.info.copy()
        del info['metadata_backend_config']
        del info['owner_tag']
        del info['cluster_cache_handle']
        info['devicename'] = disk.devicename
        disks.append(info)
    return disks

if __name__ == '__main__':
    import pprint
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-p', '--path', help='Volume path')
    options = parser.parse_args()
    pprint.pprint(action([options.path]))
