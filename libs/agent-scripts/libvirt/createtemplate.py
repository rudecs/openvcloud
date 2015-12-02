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
    import time
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList
    from ovs.dal.hybrids.vdisk import VDisk
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from CloudscalerLibcloud import imageutil
    connection = LibvirtUtil()
    filename = '%s_%s.raw' % (name, time.time())
    # create disk in ovs model so we dont get double disks
    vdisk = VDisk()
    vdisk.devicename = 'templates/%s' % filename
    vdisk.vpool = VPoolList.get_vpool_by_name('vmstor')
    vdisk.size = 0
    vdisk.save()

    # clone disk
    try:
        imagepath = connection.exportToTemplate(machineid, templatename, createfrom, filename)
        size = int(j.system.platform.qemu_img.info(imagepath, unit='')['virtual size'])
        fd = os.open(imagepath, os.O_RDWR | os.O_CREAT)
        os.ftruncate(fd, size)
        os.close(fd)
    except:
        vdisk.delete()
        raise

    # set disks as template in ovs
    imagebasename = j.system.fs.getBaseName(imagepath)
    diskguid = imageutil.setAsTemplate(imagebasename).replace('-', '')

    # update our model
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
        cimage = dict()
        cimage['name'] = templatename
        cimage['id'] = diskguid
        cimage['UNCPath'] = imagename
        cimage['type'] = 'Custom Templates'
        cimage['size'] = 0
        catimageclient.set(cimage)

    # register node if needed and update images on it
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
    return image.dump()

if __name__ == '__main__':
    action('7ecf9fa8-de38-4dc5-8f4c-2d96c09b236a', 'test', 10, None)