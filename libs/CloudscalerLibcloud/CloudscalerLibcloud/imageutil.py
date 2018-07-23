from JumpScale import j
from CloudscalerLibcloud import openvstorage


def registerImage(service, name, type, disksize, username=None, bootType='bios', delete=True, hotResize=True):
    srcpath = None
    for export in service.hrd.getListFromPrefix('service.web.export'):
        srcpath = export['dest']
    if not srcpath:
        raise RuntimeError("No image export defined in service")

    templateguid, imagepath = openvstorage.copyImage(srcpath)
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
        image.bootType = bootType
        image.hotResize = hotResize
        imageId, _, _ = ccl.image.set(image)
        ccl.stack.updateSearch({'gid': image.gid}, {'$addToSet': {'images': imageId}})
    # successfully registered lets delete source file
    if delete:
        j.system.fs.remove(srcpath)

    return True
