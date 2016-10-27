from JumpScale import j
from CloudscalerLibcloud import openvstorage


def registerImage(service, name, type, disksize, username=None):
    imagepath = None
    for export in service.hrd.getListFromPrefix('service.web.export'):
        imagepath = export['dest']
    if not imagepath:
        raise RuntimeError("No image export defined in service")

    templateguid, imagepath = openvstorage.copyImage(imagepath)
    templateguid = templateguid.replace('-', '')  # osis strips dashes
    # register image on cloudbroker
    lcl = j.clients.osis.getNamespace('libvirt')
    ccl = j.clients.osis.getNamespace('cloudbroker')

    installed_images = lcl.image.list()
    if templateguid not in installed_images:
        image = dict()
        image['name'] = name
        image['id'] = templateguid
        image['gid'] = j.application.whoAmI.gid
        image['UNCPath'] = imagepath
        image['type'] = type
        image['size'] = disksize
        image['username'] = username
        lcl.image.set(image)

    images = ccl.image.search({'referenceId': templateguid})[1:]
    if not images:
        image = ccl.image.new()
        image.name = name
        image.referenceId = templateguid
        image.type = type
        image.size = disksize
        image.username = username
        image.gid = j.application.whoAmI.gid
        image.provider_name = 'libvirt'
        image.status = 'CREATED'
        ccl.image.set(image)

    return True
