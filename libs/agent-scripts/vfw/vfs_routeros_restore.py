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
    scl = j.clients.osis.getNamespace('system')
    grid = scl.grid.get(j.application.whoAmI.gid)
    ovs_credentials = grid.settings.get('ovs_credentials', {})
    edgeuser = ovs_credentials.get('edgeuser')
    edgepassword = ovs_credentials.get('edgepassword')
    edgeip, edgeport, edgetransport = acl.execute('greenitglobe', 'getedgeconnection',
                                                  role='storagedriver', gid=j.application.whoAmI.gid)
    localfile = '/var/lib/libvirt/images/routeros/{:04x}/routeros.qcow2'.format(networkid)
    devicename = 'routeros/{0:04x}/routeros-small-{0:04x}'.format(networkid)
    ovslocation = 'openvstorage+%s:%s:%s/%s' % (
        edgetransport, edgeip, edgeport, devicename
    )
    if edgeuser:
        ovslocation += ":username={}:password={}".format(edgeuser, edgepassword)
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
