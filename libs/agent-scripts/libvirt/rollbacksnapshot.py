from JumpScale import j

descr = """
Rollback a snapshot on a machine
"""

name = "rollbacksnapshot"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@incubaid.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(diskpaths, timestamp):
    from CloudscalerLibcloud import openvstorage
    from ovs.lib.vdisk import VDiskController

    for diskpath in diskpaths:
        disk = openvstorage.getVDisk(diskpath)
        for snap in disk.snapshots:
            if snap['timestamp'] == str(timestamp):
                VDiskController.rollback(disk.guid, snap['timestamp'])

    return True

if __name__ == '__main__':
    from JumpScale.baselib import cmdutils
    parser = cmdutils.ArgumentParser()
    parser.add_argument('-p', '--path', help='Volume Path')
    parser.add_argument('-t', '--timestamp', help='Snapshot timestamp')
    options = parser.parse_args()
    action([options.path], options.timestamp)

