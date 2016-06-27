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
    from CloudscalerLibcloud import openvstorage

    snapshots = set()
    for diskpath in diskpaths:
        disk = openvstorage.getVDisk(diskpath)
        if disk:
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
