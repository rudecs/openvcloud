
from JumpScale import j

descr = """
Restore routeros
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
enable = True
async = True
queue = 'hypervisor'


def action(networkid):
    acl = j.clients.agentcontroller.get()
    edgeip, edgeport, edgetransport = acl.execute('greenitglobe', 'getedgeconnection',
                                                  role='storagedriver', gid=j.application.whoAmI.gid)
    localfile = '/var/lib/libvirt/images/routeros/{:04x}/routeros.qcow2'.format(networkid)
    devicename = 'routeros/{0:04x}/routeros-small-{0:04x}'.format(networkid)
    ovslocation = 'openvstorage+%s:%s:%s/%s' % (
        edgetransport, edgeip, edgeport, devicename
    )
    print('Restoring {} to {}'.format(ovslocation, localfile))
    destination = '/var/lib/libvirt/images/routeros/'
    networkidHex = '%04x' % int(networkid)
    try:
        j.system.platform.qemu_img.info(ovslocation)
    except RuntimeError as e:
        if 'No such file or directory' in e.message:
            return False
        j.errorconditionhandler.processPythonExceptionObject(e)
        return False
    if j.system.fs.exists(j.system.fs.joinPaths(destination, networkidHex)):
        j.system.btrfs.subvolumeDelete(destination, networkidHex)
    j.system.btrfs.subvolumeCreate(destination, networkidHex)
    try:
        j.system.platform.qemu_img.convert(ovslocation, 'raw', localfile, 'qcow2')
    except Exception as e:
        j.system.btrfs.subvolumeDelete(destination, networkidHex)
        j.errorconditionhandler.processPythonExceptionObject(e)
        return False
    return True
