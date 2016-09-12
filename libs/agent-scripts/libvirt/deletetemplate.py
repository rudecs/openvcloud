from JumpScale import j

descr = """
Libvirt script to create template
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(imageId):
    import sys
    import os
    import uuid
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.vdisklist import VDisk
    lcl = j.clients.osis.getNamespace('libvirt')

    diskguid = uuid.UUID(imageId)
    try:
        disk = VDisk(diskguid)
    except:
        disk = None
    if disk:
        if len(disk.child_vdisks) != 0:
            return -1
        path = os.path.join('/mnt/vmstor', disk.devicename)
        j.system.fs.remove(path)
    lcl.image.delete(imageId)
    for resource in lcl.resourceprovider.search({'images': imageId})[1:]:
        resource['images'].remove(imageId)
        lcl.resourceprovider.set(resource)
    return True

