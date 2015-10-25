from JumpScale import j

descr = """
Libvirt script to create a volume
"""

name = "createvolume"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(name, size):
    import sys
    import os
    sys.path.append('/opt/OpenvStorage')
    from ovs.lib.vdisk import VDiskController
    from ovs.dal.lists.vpoollist import VPoolList
    from ovs.dal.hybrids.vdisk import VDisk
    
    volumepath = '/mnt/vmstor/volumes'
    
    vdisk = VDisk()
    vdisk.name = name
    vdisk.devicename = j.system.fs.joinPaths(volumepath, 'volume_%s.raw' % name)
    vdisk.vpool = VPoolList.get_vpool_by_name('vmstor')
    vdisk.size = size
    vdisk.save()
    params = {
        'dtl_mode': 'async',
        'sco_size': 64,
        'dedupe_mode': 'dedupe',
        'dtl_enabled': False,
        'write_buffer': 1024,
        'cache_strategy': 'on_read',
        'readcache_limit': 10}
    
    VDiskController.set_config_params(vdisk.guid, params)
    
    j.system.fs.createDir(volumepath)
    filepath = j.system.fs.joinPaths(volumepath, 'volume_%s.raw' % name)
    fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
    os.ftruncate(fd, size)
    os.close(fd)
    return filepath

if __name__ == '__main__':
    action('hamdy_testdisk', 20)