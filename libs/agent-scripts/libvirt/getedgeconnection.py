from JumpScale import j

descr = """
Libvirt script to create a disk
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
async = True


def action():
    from CloudscalerLibcloud import openvstorage
    return openvstorage.getEdgeconnection()

