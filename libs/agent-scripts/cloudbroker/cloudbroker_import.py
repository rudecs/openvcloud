from JumpScale import j

descr = """
Follow up creation of import
"""

name = "cloudbroker_import"
category = "cloudbroker"
organization = "greenitglobe"
author = "elawadim@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
queue = 'io'
async = True
timeout = 60 * 60


def action(link, username, passwd, path, machine):
    from CloudscalerLibcloud import openvstorage
    from CloudscalerLibcloud.utils import webdav
    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        filename = '%s/ovf.tar.gz' % tmpdir
        webdav.download_file(link, username, passwd, path, filename)
        ovfpath = '%s/ovf' % tmpdir

        j.system.fs.targzUncompress(filename, ovfpath)

        bootdisk = '%s/%s' % (ovfpath, machine['disks'][0]['path'])
        datadisks = map(lambda x: '%s/%s' % (ovfpath, x['path']), machine['disks'][1:])

        bootres = [openvstorage.importVolume(bootdisk, "vm-%d/bootdisk-vm-%d.raw" % (machine['id'], machine['id']), False)]
        datares = [openvstorage.importVolume(disk,
                    "volumes/volume_%d.raw" % (disk['id']), True) for disk in datadisks]
        res = bootres + datares
        for disk, job in zip(machine['disks'], res):
            disk['guid'], disk['path'] = job
        return machine
    finally:
        j.system.fs.removeDirTree(tmpdir)
        # TODO: remove imported disks in case of falure

if __name__ == "__main__":
    print(action('a', 'a', 'a', 'a', {
        'id': 5555,
        'disks': [{
            'id': '6666',
            'path': 'disk-0.vmdk'
        }]
    }))
