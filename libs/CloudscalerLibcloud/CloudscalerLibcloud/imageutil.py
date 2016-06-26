from JumpScale import j
from CloudscalerLibcloud import openvstorage

def registerImage(service, name, type, disksize, username=None):
    imagepath = None
    for export in service.hrd.getListFromPrefix('service.web.export'):
        imagepath = export['dest']
    if not imagepath:
        raise RuntimeError("No image export defined in service")

    templateguid, imagepath = openvstorage.copyImage(imagepath)
    templateguid = templateguid.replace('-', '') # osis strips dashes
    #register image on cloudbroker
    node_id = "%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid)
    osiscl = j.clients.osis.getByInstance('main')
    lcl = j.clients.osis.getNamespace('libvirt')
    ccl = j.clients.osis.getNamespace('cloudbroker')

    installed_images = lcl.image.list()
    if templateguid not in installed_images:
        image = dict()
        image['name'] = name
        image['id'] = templateguid
        image['UNCPath'] = imagepath
        image['type'] = type
        image['size'] = disksize
        image['username'] = username
        lcl.image.set(image)

    if not node_id in lcl.resourceprovider.list():
        rp = dict()
        rp['cloudUnitType'] = 'CU'
        rp['id'] = str(j.application.whoAmI.nid)
        rp['gid'] = j.application.whoAmI.gid
        rp['images'] = [templateguid]
    else:
        rp = lcl.resourceprovider.get(node_id)
        if not templateguid in rp.images:
            rp.images.append(templateguid)
    lcl.resourceprovider.set(rp)

    images = ccl.image.search({'referenceId': templateguid})[1:]
    if not images:
        image = ccl.image.new()
        image.name = name
        image.referenceId = templateguid
        image.type = type
        image.size = disksize
        image.username = username
        image.provider_name = 'libvirt'
        image.status = 'CREATED'
        imageId = ccl.image.set(image)[0]
    else:
        imageId = images[0]['id']
    stacks = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid)})[1:]
    if stacks:
        stack = stacks[0]
        if imageId not in stack.get('images', []):
            stack.setdefault('images', []).append(imageId)
            ccl.stack.set(stack)

    return True
