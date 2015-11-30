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


def action(diskpaths):
    import sys
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    snapshots = set()
    pool = VPoolList.get_vpool_by_name('vmstor')
    for diskpath in diskpaths:
        diskpath = diskpath.replace('/mnt/vmstor/', '')
        disk = VDiskList.get_by_devicename_and_vpool(diskpath, pool)
        for snap in disk.snapshots:
            if not snap['is_automatic']:
                snapshots.add((snap['label'], int(snap['timestamp'])))
    snaps = list()
    for snap in snapshots:
        snaps.append({'name': snap[0], 'epoch':snap[1]})
    return snaps


if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-p', '--path', help='Volume Path')
    options = parser.parse_args()
    print action([options.path])
