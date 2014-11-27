from JumpScale import j
import JumpScale.grid.osis
import requests

def registerImage(jp, name, imagepath, type, disksize, username = None):
    #register image on cloudbroker
    node_id = "%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid)
    image_id = str(int(j.tools.hash.md5_string(jp.name)[0:9], 16))
    osiscl = j.core.osis.getClientByInstance('main')
    catimageclient = j.core.osis.getClientForCategory(osiscl, 'libvirt', 'image')
    catresourceclient = j.core.osis.getClientForCategory(osiscl, 'libvirt', 'resourceprovider')

    installed_images = catimageclient.list()
    if image_id not in installed_images:
        image = dict()
        image['name'] = name
        image['id'] = image_id
        image['UNCPath'] = imagepath
        image['type'] = type
        image['size'] = disksize
        image['username'] = username
        catimageclient.set(image)


    if not node_id in catresourceclient.list():
        rp = dict()
        rp['cloudUnitType'] = 'CU'
        rp['id'] = str(j.application.whoAmI.nid)
        rp['gid'] = j.application.whoAmI.gid
        rp['images'] = [image_id]
    else:
        rp = catresourceclient.get(node_id)
        if not image_id in rp.images:
            rp.images.append(image_id)
    catresourceclient.set(rp)

    return True
