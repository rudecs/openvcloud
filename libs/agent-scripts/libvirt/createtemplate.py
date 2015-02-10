from JumpScale import j

descr = """
Libvirt script to create a machine
"""

name = "createtemplate"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid, templatename, imageid, createfrom):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    image_id, imagepath = connection.exportToTemplate(machineid, templatename, createfrom)
    osiscl = j.clients.osis.getByInstance('main')
    imagemodel = j.clients.osis.getCategory(osiscl, 'cloudbroker', 'image')
    image = imagemodel.get(imageid)
    image.referenceId = image_id
    image.status = 'CREATED'
    imagemodel.set(image)

    catimageclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'image')
    catresourceclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'resourceprovider')

    imagename = j.system.fs.getBaseName(imagepath)
    installed_images = catimageclient.list()
    if image_id not in installed_images:
        image = dict()
        image['name'] = templatename
        image['id'] = image_id
        image['UNCPath'] = imagename
        image['type'] = 'custom templates'
        image['size'] = 0
        catimageclient.set(image)

    nodekey = "%(gid)s_%(nid)s" % j.application.whoAmI._asdict()
    if not catresourceclient.exists(nodekey):
        rp = dict()
        rp['cloudUnitType'] = 'CU'
        rp['id'] = j.application.whoAmI.nid
        rp['gid'] = j.application.whoAmI.gid
        rp['guid'] = nodekey
        rp['images'] = [image_id]
    else:
        rp = catresourceclient.get(nodekey)
        if not image_id in rp.images:
            rp.images.append(image_id)
    catresourceclient.set(rp)
    return image
