from JumpScale import j


descr = """
Libvirt script to create a volume
"""

name = "createvolumes"
category = "libvirt"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(volumes):
    import os

    for volume in volumes:
        volumepath = '/mnt/vmstor/volumes'
        j.system.fs.createDir(volumepath)
        filepath = j.system.fs.joinPaths(volumepath, 'volume_%(name)s.raw' % volume)
        volume['id'] = filepath
        fd = os.open(filepath, os.O_RDWR | os.O_CREAT)
        os.ftruncate(fd, volume['size'])
        os.close(fd)

    def setConfigs(volumes):
        import sys
        import time
        sys.path.append('/opt/OpenvStorage')
        from ovs.lib.vdisk import VDiskController
        from ovs.dal.lists.vpoollist import VPoolList
        from ovs.dal.lists.vdisklist import VDiskList
        params = {
            'dtl_mode': 'a_sync',
            'sco_size': 64,
            'dedupe_mode': 'non_dedupe',
            'dtl_enabled': False,
            'dtl_target': j.system.net.getIpAddress('backplane1')[0][0],
            'write_buffer': 1024,
            'cache_strategy': 'on_read',
            'readcache_limit': 10}
        pool = VPoolList.get_vpool_by_name('vmstor')
        for volume in volumes:
            vdisk = None
            while not vdisk:
                time.sleep(0.1)
                vdisk = VDiskList.get_by_devicename_and_vpool('volumes/volume_%(name)s.raw' % volume, pool)
            VDiskController.set_config_params(vdisk.guid, params)
    j.clients.redisworker.execFunction(setConfigs, _queue='io', _sync=False, volumes=volumes)
    return volumes

if __name__ == '__main__':
    action('hamdy_testdisk', 20)
