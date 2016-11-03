from JumpScale import j
import sys
import random
import os
import time
import urlparse
import tempfile

sys.path.append('/opt/OpenvStorage')
from ovs.lib.vdisk import VDiskController
from ovs.dal.lists.vdisklist import VDiskList
from ovs.dal.lists.vpoollist import VPoolList
from ovs.dal.lists.storagerouterlist import StorageRouterList
from ovs.dal.lists.storagedriverlist import StorageDriverList

VPOOLNAME = 'vmstor'


def setAsTemplate(templatepath):
    disk = getVDisk(templatepath, timeout=60)
    if not disk:
        raise RuntimeError("Template did not become available on OVS at %s" % templatepath)
    if disk.info['object_type'] != 'TEMPLATE':
        VDiskController.set_as_template(disk.guid)
    return disk.guid


def listEdgeclients():
    edgeclients = []
    protocol = getEdgeProtocol()
    for storagerouter in StorageRouterList.get_storagerouters():
        if storagerouter.status == 'FAILURE':
            continue
        for storagedriver in storagerouter.storagedrivers:
            edgeclient = {'vpool': storagedriver.vpool.name,
                          'protocol': protocol,
                          'ip': storagerouter.ip,
                          'port': storagedriver.ports['edge']}
            edgeclients.append(edgeclient)
    return edgeclients


def getEdgeProtocol():
    try:
        from ovs.extensions.generic.configuration import Configuration
        if Configuration.get('/ovs/framework/rdma'):
            return 'rdma'
        else:
            return 'tcp'
    except:
        return 'tcp'


def getLocalStorageRouter():
    localips = j.system.net.getIpAddresses()
    for storagerouter in StorageRouterList.get_storagerouters():
        if storagerouter.ip in localips:
            return storagerouter


def getEdgeconnection(vpoolname=VPOOLNAME):
    protocol = getEdgeProtocol()
    storagedrivers = list(StorageDriverList.get_storagedrivers())
    random.shuffle(storagedrivers)
    if vpoolname is None:
        if storagedrivers[0].vpool.name != VPOOLNAME:
            storagedriver = storagedrivers[0]
        else:
            storagedriver = storagedrivers[1]
        return storagedriver.storage_ip, storagedriver.ports['edge'], protocol
    for storagedriver in storagedrivers:
        if storagedriver.vpool.name == vpoolname:
            return storagedriver.storage_ip, storagedriver.ports['edge'], protocol
    return None, None, protocol


def getVPoolByIPandPort(ip, port):
    for storagerouter in StorageRouterList.get_storagerouters():
        for storagedriver in storagerouter.storagedrivers:
            if storagedriver.ports['edge'] == port and storagedriver.storage_ip == ip:
                return storagedriver.vpool
    raise RuntimeError("Could not find vpool for {}:{}".format(ip, port))


def _getVPoolByUrl(url, vpoolname=None):
    if vpoolname is None and url.port:
        vpool = getVPoolByIPandPort(url.hostname, url.port)
    elif vpoolname is None:
        vpool = VPoolList.get_vpool_by_name(VPOOLNAME)
    else:
        vpool = VPoolList.get_vpool_by_name(vpoolname)
    return vpool


def getVDisk(path, vpool=None, timeout=None):
    url = urlparse.urlparse(path)
    path = '/' + url.path.strip('/')
    if not path.endswith('.raw'):
        path += '.raw'
    elif not url.scheme:
        parts = url.path.split('/')[1:]  # remove first slash
        if parts[0] == 'mnt':
            vpool = parts[1]
            path = '/' + '/'.join(parts[2:])

    vpool = _getVPoolByUrl(url, vpool)
    disk = VDiskList.get_by_devicename_and_vpool(path, vpool)
    if timeout is not None:
        start = time.time()
        while not disk and start + timeout > time.time():
            time.sleep(2)
            disk = VDiskList.get_by_devicename_and_vpool(path, vpool)
    return disk


def getUrlPath(path, vpoolname=VPOOLNAME):
    storageip, edgeport, protocol = getEdgeconnection(vpoolname)
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


def getPath(path, vpoolname=None):
    """ Get path from referenceId of VM"""
    url = urlparse.urlparse(path)
    vpool = _getVPoolByUrl(url, vpoolname)
    path = url.path.strip('/')
    pathparts = path.split('/')
    if pathparts[0] == 'mnt':
        path = '/'.join(pathparts[2:])
    if not path.startswith('/mnt/%s' % vpool.name):
        path = os.path.join('/mnt/%s' % vpool.name, path)

    # Strip vdiskguid from path
    head, sep, tail = path.partition('@')
    path = head

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


def importVolume(srcpath, destpath, data=False):
    if data:
        dest = getUrlPath(destpath, vpoolname=None)
    else:
        dest = getUrlPath(destpath, vpoolname=VPOOLNAME)
    j.system.platform.qemu_img.convert(srcpath, None, dest.replace('://', ':', 1), 'raw')
    disk = getVDisk(destpath, timeout=60)
    return disk.guid, dest


def exportVolume(srcpath, destpath):
    j.system.platform.qemu_img.convert(srcpath.replace('://', ':', 1), None, destpath, 'vmdk')
    return destpath


class TempStorage(object):

    BASE = '/mnt/%s/tmp' % VPOOLNAME

    def __enter__(self):
        j.system.fs.createDir(self.BASE)
        raw = tempfile.mktemp('.raw', dir=self.BASE)
        self.raw = raw
        truncate(raw, 2 * 1024 * 1024 * 1024 * 1024)
        res = os.system('mkfs -t btrfs "%s"' % raw)
        if res:
            self.__exit__()
            raise RuntimeError('Cannot make file system for the raw device')
        path = j.system.fs.getTmpDirPath()
        self.path = path
        res = os.system('mount -t btrfs -o loop "%s" "%s"' % (raw, path))
        if res:
            self.__exit__()
            raise RuntimeError('Cannot mount loop device')
        return self

    def __exit__(self, *args, **kwargs):
        raw = self.raw
        path = self.path
        os.system('umount "%s"' % path)
        j.system.fs.removeDirTree(path)
        getVDisk(self.path, timeout=10)
        j.system.fs.remove(raw)


def truncate(filepath, size=None):
    if size is None:
        size = os.stat(filepath).st_size
    fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
    try:
        os.ftruncate(fd, size)
    finally:
        os.close(fd)
