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
    from CloudscalerLibcloud import openvstorage

    for volume in volumes:
        volumepath = 'volumes/volume_{name}.raw'.format(**volume)
        filepath = openvstorage.getPath(volumepath)
        j.system.fs.createDir(j.system.fs.getDirName(filepath))
        volume['id'] = openvstorage.getUrlPath(volumepath)
        openvstorage.truncate(filepath, volume['size'])

    def setConfigs(volumes):
        from CloudscalerLibcloud import openvstorage
        import time
        from ovs.lib.vdisk import VDiskController
        params = {
            'dtl_mode': 'a_sync',
            'sco_size': 64,
            'dedupe_mode': 'non_dedupe',
            'dtl_enabled': False,
            'dtl_target': j.system.net.getIpAddress('backplane1')[0][0],
            'write_buffer': 1024,
            'cache_strategy': 'on_read',
            'readcache_limit': 10}
        timeout = 120
        start = time.time()
        for volume in volumes:
            vdisk = None
            while not vdisk and start + timeout > time.time():
                time.sleep(0.1)
                vdisk = openvstorage.getVDisk(volume['id'])
            if not vdisk:
                raise RuntimeError("Could not find volume %s on OVS backend" % volume)
            VDiskController.set_config_params(vdisk.guid, params)
    j.clients.redisworker.execFunction(setConfigs, _queue='io', _sync=False, volumes=volumes)
    return volumes

if __name__ == '__main__':
    size = 1024**4
    action({'name': 'test', 'size': size})
