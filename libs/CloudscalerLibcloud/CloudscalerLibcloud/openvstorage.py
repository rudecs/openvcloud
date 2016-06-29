from JumpScale import j
import sys
import os
import time
import urlparse
sys.path.append('/opt/OpenvStorage')
from ovs.lib.vdisk import VDiskController
from ovs.dal.lists.vdisklist import VDiskList
from ovs.dal.lists.vpoollist import VPoolList
from ovs.dal.lists.storagerouterlist import StorageRouterList

def setAsTemplate(templatepath):
    pool = VPoolList.get_vpool_by_name('vmstor')
    disk = None
    start = time.time()
    while not disk and start + 60 > time.time():
        time.sleep(2)
        disk = VDiskList.get_by_devicename_and_vpool(templatepath, pool)
    if not disk:
        raise RuntimeError("Template did not become available on OVS at %s" % templatepath)
    if disk.info['object_type'] != 'TEMPLATE':
        VDiskController.set_as_template(disk.guid)
    return disk.guid


def getEdgeconnection():
    localips = j.system.net.getIpAddresses()
    for storagerouter in StorageRouterList.get_storagerouters():
        if storagerouter.ip in localips:
            protocol = 'rdma' if storagerouter.rdma_capable else 'tcp'
            for storagedriver in storagerouter.storagedrivers:
                return storagedriver.storage_ip, storagedriver.ports['edge'], protocol
    return None, None, None


def getVDisk(path, vpool=None):
    url = urlparse.urlparse(path)
    path = url.path.strip('/')
    if not path.endswith('.raw'):
        path += '.raw'
    if vpool is None:
        vpool = VPoolList.get_vpool_by_name('vmstor')
    return VDiskList.get_by_devicename_and_vpool(path, vpool)

def getUrlPath(path):
    storageip, edgeport, protocol = getEdgeconnection()
    newpath, ext = os.path.splitext(path)
    if ext != '.raw':
        newpath = path
    newpath = newpath.strip('/')
    if not storageip:
        raise RuntimeError("Could not find edge connection")
    return "openvstorage+{protocol}://{ip}:{port}/{name}".format(protocol=protocol,
                                                                 ip=storageip,
                                                                 port=edgeport,
                                                                 name=newpath)

def getPath(path):
    url = urlparse.urlparse(path)
    path = url.path.strip('/')
    if not path.startswith('/mnt/vmstor'):
        path = os.path.join('/mnt/vmstor', path)
    if not path.endswith('.raw'):
        path += '.raw'
    return path

def copyImage(srcpath):
    imagename = os.path.splitext(j.system.fs.getBaseName(srcpath))[0]
    templatepath = 'templates/%s.raw' % imagename
    dest = getUrlPath("templates/%s" % imagename)
    if not getVDisk(templatepath):
        j.system.platform.qemu_img.convert(srcpath, None, dest.replace('://', ':', 1), 'raw')
        truncate(getPath(templatepath))
    diskguid = setAsTemplate(templatepath)
    return diskguid, dest

def truncate(filepath, size=None):
    if size is None:
        size = os.stat(filepath).st_size
    fd = os.open(filepath, os.O_RDWR|os.O_CREAT)
    try:
        os.ftruncate(fd, size)
    finally:
        os.close(fd)
