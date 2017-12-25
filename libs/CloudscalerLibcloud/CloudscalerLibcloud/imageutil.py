from JumpScale import j
from CloudscalerLibcloud import openvstorage


def registerImage(service, name, type, disksize, username=None):
    imagepath = None
    for export in service.hrd.getListFromPrefix('service.web.export'):
        imagepath = export['dest']
    if not imagepath:
        raise RuntimeError("No image export defined in service")

    templateguid, imagepath = openvstorage.copyImage(imagepath)
    # register image on cloudbroker
    ccl = j.clients.osis.getNamespace('cloudbroker')

    if ccl.image.count({'referenceId': templateguid}) == 0:
        image = ccl.image.new()
        image.name = name
        image.referenceId = templateguid
        image.type = type
        image.size = disksize
        image.username = username
        image.gid = j.application.whoAmI.gid
        image.provider_name = 'libvirt'
        image.UNCPath = imagepath
        image.status = 'CREATED'
        imageId, _, _ = ccl.image.set(image)
        ccl.stack.updateSearch({'gid': image.gid}, {'$addToSet': {'images': imageId}})

    return True
