from JumpScale import j
import JumpScale.grid.osis
import requests
import sys


def copyImageToOVS(imagepath):
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList

    newimagepath = imagepath.replace('.qcow2', '.raw')
    dstdir = '/mnt/vmstor/templates'
    j.system.fs.createDir(dstdir)
    src = j.system.fs.joinPaths('/opt/jumpscale7/var/tmp/templates/', imagepath)
    dst = j.system.fs.joinPaths(dstdir, newimagepath)

    if not j.system.fs.exists(dst):
        j.system.platform.qemu_img.convert(src, 'qcow2', dst, 'raw')

    pool = VPoolList.get_vpool_by_name('vmstor')
    disk = VDiskList.get_by_devicename_and_vpool('templates/%s' % newimagepath, pool)
    VDiskController.set_as_template(disk.guid)
    return disk.guid, newimagepath

def registerImage(jp, name, imagepath, type, disksize, username=None):
    templateguid, imagepath = copyImageToOVS(imagepath)
    #register image on cloudbroker
    node_id = "%s_%s" % (j.application.whoAmI.gid, j.application.whoAmI.nid)
    osiscl = j.clients.osis.getByInstance('main')
    catimageclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'image')
    catresourceclient = j.clients.osis.getCategory(osiscl, 'libvirt', 'resourceprovider')

    installed_images = catimageclient.list()
    if templateguid not in installed_images:
        image = dict()
        image['name'] = name
        image['id'] = templateguid
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
        rp['images'] = [templateguid]
    else:
        rp = catresourceclient.get(node_id)
        if not templateguid in rp.images:
            rp.images.append(templateguid)
    catresourceclient.set(rp)

    return True
