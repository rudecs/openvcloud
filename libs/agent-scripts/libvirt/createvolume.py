from JumpScale import j


descr = """
Libvirt script to create a volume
"""

category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(volume, edgeclient):
    from CloudscalerLibcloud import openvstorage
    volumepath = 'volumes/volume_{name}.raw'.format(**volume)
    filepath = openvstorage.getPath(volumepath, edgeclient['vpool'])
    j.system.fs.createDir(j.system.fs.getDirName(filepath))
    volume['id'] = openvstorage.getUrlPath(volumepath, edgeclient['vpool'])
    openvstorage.truncate(filepath, volume['size'])
    return volume

if __name__ == '__main__':
    size = 1024**4
    action({'name': 'test', 'size': size}, {'vpool': 'vmstor'})
