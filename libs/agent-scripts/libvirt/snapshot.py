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


def action(diskpaths, name):
    import sys
    import time
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    meta = {'label': name,
            'is_consistent': False,
            'is_automatic': False,
            'timestamp': str(int(time.time()))}

    pool = VPoolList.get_vpool_by_name('vmstor')
    for diskpath in diskpaths:
        diskpath = diskpath.replace('/mnt/vmstor/', '')
        disk = VDiskList.get_by_devicename_and_vpool(diskpath, pool)
        VDiskController.create_snapshot(diskguid=disk.guid, metadata=meta)

    return {'name': name}

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-n', '--name', help='Snapshot name')
    parser.add_argument('-p', '--path', help='Volume path')
    options = parser.parse_args()
    action([options.path], options.name)

