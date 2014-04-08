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
roles = ["*"]
async = True


def action(machineid, templatename, imageid, createfrom):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    image_id, imagepath = connection.exportToTemplate(machineid, templatename, createfrom)
    osisserver  = j.application.config.get('grid.master.ip')
    user = j.application.config.get('system.superadmin.login')
    osiscl = j.core.osis.getClient(ipaddr=osisserver, user=user)
    imagemodel = j.core.osis.getClientForCategory(osiscl, 'cloudbroker', 'image')
    image = imagemodel.get(imageid)
    image.referenceId = image_id
    image.status = 'CREATED'
    imagemodel.set(image)

    catimageclient = j.core.osis.getClientForCategory(osiscl, 'libvirt', 'image')
    catresourceclient = j.core.osis.getClientForCategory(osiscl, 'libvirt', 'resourceprovider')

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

    node_id = j.application.config.get("cloudscalers.compute.nodeid")
    if not node_id in catresourceclient.list():
        rp = dict()
        rp['cloudUnitType'] = 'CU'
        rp['id'] = node_id
        rp['images'] = [image_id]
    else:
        rp = catresourceclient.get(node_id)
        if not image_id in rp.images:
            rp.images.append(image_id)
    catresourceclient.set(rp)



