from JumpScale import j
import sys
import os
import time
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
    if vpool is None:
        vpool = VPoolList.get_vpool_by_name('vmstor')
    return VDiskList.get_by_devicename_and_vpool(path, vpool)

def copyImage(srcpath):
    # qemu-img convert volume1.qcow2 openvstorage+tcp:127.0.0.1:12329/volume3
    imagename = os.path.splitext(j.system.fs.getBaseName(srcpath))[0]
    templatepath = 'templates/%s.raw' % imagename
    if not getVDisk(templatepath):
        storageip, edgeport, protocol = getEdgeconnection()
        if not storageip:
            raise RuntimeError("Could not find edge connection")
        dest = "openvstorage+{protocol}:{ip}:{port}/templates/{name}".format(protocol=protocol,
                                                                             ip=storageip,
                                                                             port=edgeport,
                                                                             name=imagename)
        j.system.platform.qemu_img.convert(srcpath, None, dest, 'raw')
    diskguid = setAsTemplate(templatepath)
    return diskguid, templatepath
