from JumpScale import j

descr = """
Libvirt script to list existing vpools
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action():
    from CloudscalerLibcloud import openvstorage
    return list(openvstorage.listEdgeclients())
