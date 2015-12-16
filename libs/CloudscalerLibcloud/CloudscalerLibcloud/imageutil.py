from JumpScale import j
import JumpScale.grid
import os
import sys
import time

def setAsTemplate(imagepath):
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vdisklist import VDiskList
    from ovs.dal.lists.vpoollist import VPoolList
    pool = VPoolList.get_vpool_by_name('vmstor')
    disk = None
    start = time.time()
    while not disk and start + 60 > time.time():
        time.sleep(2)
        disk = VDiskList.get_by_devicename_and_vpool('templates/%s' % imagepath, pool)
    if disk.info['object_type'] != 'TEMPLATE':
        VDiskController.set_as_template(disk.guid)
    return disk.guid

def copyImageToOVS(imagepath):

    newimagepath = imagepath.replace('.qcow2', '.raw')
    dstdir = '/mnt/vmstor/templates'
    j.system.fs.createDir(dstdir)
    src = j.system.fs.joinPaths('/opt/jumpscale7/var/tmp/templates/', imagepath)
    dst = j.system.fs.joinPaths(dstdir, newimagepath)

    if not j.system.fs.exists(dst):
        j.system.platform.qemu_img.convert(src, 'qcow2', dst, 'raw')
        size = int(j.system.platform.qemu_img.info(dst, unit='')['virtual size'])
        fd = os.open(dst, os.O_RDWR | os.O_CREAT)
        os.ftruncate(fd, size)
        os.close(fd)
    diskguid = setAsTemplate(newimagepath)
    return diskguid, newimagepath

def registerImage(jp, name, imagepath, type, disksize, username=None):
    templateguid, imagepath = copyImageToOVS(imagepath)
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
        image.status = 'CREATED'
        imageId = ccl.image.set(image)[0]
    else:
        imageId = images[0]['id']
    stacks = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid)})[1:]
    if stacks:
        stack = stacks[0]
        if imageId not in stack['images']:
            stack['images'].append(imageId)
            ccl.stack.set(stack)


    return True
