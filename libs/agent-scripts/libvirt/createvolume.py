from JumpScale import j

descr = """
Libvirt script to create a volume
"""

name = "createvolume"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(name, size):
    import sys
    import os
    volumepath = '/mnt/vmstor/volumes'
    j.system.fs.createDir(volumepath)
    filepath = j.system.fs.joinPaths(volumepath, 'volume_%s.raw' % name)
    fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
    os.ftruncate(fd, size)
    os.close(fd)
    return filepath
