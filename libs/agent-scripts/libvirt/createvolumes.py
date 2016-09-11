from JumpScale import j


descr = """
Libvirt script to create a volume
"""

name = "createvolumes"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(volumes):
    from CloudscalerLibcloud import openvstorage

    for volume in volumes:
        volumepath = 'volumes/volume_{name}.raw'.format(**volume)
        filepath = openvstorage.getPath(volumepath)
        j.system.fs.createDir(j.system.fs.getDirName(filepath))
        volume['id'] = openvstorage.getUrlPath(volumepath)
        openvstorage.truncate(filepath, volume['size'])

    return volumes

if __name__ == '__main__':
    size = 1024**4
    action({'name': 'test', 'size': size})
