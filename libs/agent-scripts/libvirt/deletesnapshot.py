from JumpScale import j

descr = """
Delete snapshot of machine
"""

name = "deletesnapshot"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(diskpaths, timestamp):
    import sys
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    pool = VPoolList.get_vpool_by_name('vmstor')
    for diskpath in diskpaths:
        diskpath = diskpath.replace('/mnt/vmstor/', '')
        disk = VDiskList.get_by_devicename_and_vpool(diskpath, pool)
        for snap in disk.snapshots:
            if snap['timestamp'] == str(timestamp):
                VDiskController.delete_snapshot(disk.guid, snap['guid'])

    return True

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-p', '--path', help='Volume Path')
    parser.add_argument('-t', '--timestamp', help='Snapshot timestamp')
    options = parser.parse_args()
    action([options.path], options.timestamp)
