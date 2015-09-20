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
    import sys
    import os
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from CloudscalerLibcloud import imageutil
    connection = LibvirtUtil()
    imagepath = connection.exportToTemplate(machineid, templatename, createfrom)
    size = int(j.system.platform.qemu_img.info(imagepath, unit='')['virtual size'])
    fd = os.open(imagepath, os.O_RDWR | os.O_CREAT)
    os.ftruncate(fd, size)
    os.close(fd)
    imagebasename = j.system.fs.getBaseName(imagepath)
    diskguid = imageutil.setAsTemplate(imagebasename).replace('-', '')
    osiscl = j.clients.osis.getByInstance('main')
    imagemodel = j.clients.osis.getCategory(osiscl, 'cloudbroker', 'image')
    image = imagemodel.get(imageid)
    image.referenceId = diskguid
    image.status = 'CREATED'
    imagemodel.set(image)

    catimageclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'image')
    catresourceclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'resourceprovider')

    imagename = j.system.fs.getBaseName(imagepath)
    installed_images = catimageclient.list()
    if diskguid not in installed_images:
        image = dict()
        image['name'] = templatename
        image['id'] = diskguid
        image['UNCPath'] = imagename
        image['type'] = 'Custom Templates'
        image['size'] = 0
        catimageclient.set(image)

    nodekey = "%(gid)s_%(nid)s" % j.application.whoAmI._asdict()
    if not catresourceclient.exists(nodekey):
        rp = dict()
        rp['cloudUnitType'] = 'CU'
        rp['id'] = j.application.whoAmI.nid
        rp['gid'] = j.application.whoAmI.gid
        rp['guid'] = nodekey
        rp['images'] = [diskguid]
    else:
        rp = catresourceclient.get(nodekey)
        if not diskguid in rp.images:
            rp.images.append(diskguid)
    catresourceclient.set(rp)
    return image

if __name__ == '__main__':
    action('7ecf9fa8-de38-4dc5-8f4c-2d96c09b236a', 'test', 10, None)