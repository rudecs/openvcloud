from JumpScale import j
import sys
import os
import time
import urlparse
import json

sys.path.append('/opt/OpenvStorage')
from ovs.lib.vdisk import VDiskController
from ovs.dal.lists.vdisklist import VDiskList
from ovs.dal.lists.vpoollist import VPoolList
from ovs.dal.lists.storagerouterlist import StorageRouterList
from ovs.dal.lists.vpoollist import VPoolList

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
        for storagedriver in storagerouter.storagedrivers:
            edgeclient = {'vpool': storagedriver.vpool.name,
                          'protocol': protocol,
                          'ip': storagerouter.ip,
                          'port': storagedriver.ports['edge']}
            edgeclients.append(edgeclient)
    return edgeclients


def getEdgeProtocol():
    import etcd
    client = etcd.Client(port=2379)
    try:
        key = client.get('/ovs/framework/rdma')
        return 'rdma' if json.loads(key.value) else 'tcp'
    except:
        return 'tcp'


def getLocalStorageRouter():
    localips = j.system.net.getIpAddresses()
    for storagerouter in StorageRouterList.get_storagerouters():
        if storagerouter.ip in localips:
            return storagerouter


def getEdgeconnection(vpoolname=VPOOLNAME):
    protocol = getEdgeProtocol()
    storagerouter = getLocalStorageRouter()
    if storagerouter:
        for storagedriver in storagerouter.storagedrivers:
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
    url = urlparse.urlparse(path)
    vpool = _getVPoolByUrl(url, vpoolname)
    path = url.path.strip('/')
    pathparts = path.split('/')
    if pathparts[0] == 'mnt':
        path = '/'.join(pathparts[2:])
    if not path.startswith('/mnt/%s' % vpool.name):
        path = os.path.join('/mnt/%s' % vpool.name, path)
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
    fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
    try:
        os.ftruncate(fd, size)
    finally:
        os.close(fd)
