from JumpScale import j

descr = """
Libvirt script to destroy a volume
"""

name = "destroyvolume"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(path):
    from CloudscalerLibcloud import openvstorage
    path = openvstorage.getPath(path)
    if j.system.fs.exists(path):
        j.system.fs.remove(path)
    return True
