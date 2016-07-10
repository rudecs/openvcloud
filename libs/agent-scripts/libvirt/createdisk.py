from JumpScale import j

descr = """
Libvirt script to create a disk
"""

name = "createdisk"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(templateguid, vmname, size):
    from CloudscalerLibcloud import openvstorage
    from ovs.lib.vdisk import VDiskController
    name = "%s/base-image" % vmname
    storagerouter = openvstorage.getLocalStorageRouter()
    data = VDiskController.create_from_template(templateguid, name=name, storagerouter_guid=storagerouter.guid)
    filepath = openvstorage.getPath(data['backingdevice'].lstrip('/'))
    openvstorage.truncate(filepath, size)
    return openvstorage.getUrlPath(data['backingdevice'])

