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
    from CloudscalerLibcloud import openvstorage
    from ovs.lib.vdisk import VDiskController
    import time

    meta = {'label': name,
            'is_consistent': False,
            'is_sticky': True,
            'is_automatic': False,
            'timestamp': str(int(time.time()))}

    for diskpath in diskpaths:
        disk = openvstorage.getVDisk(diskpath)
        VDiskController.create_snapshot(diskguid=disk.guid, metadata=meta)

    return {'name': name}

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-n', '--name', help='Snapshot name')
    parser.add_argument('-p', '--path', help='Volume path')
    options = parser.parse_args()
    action([options.path], options.name)

