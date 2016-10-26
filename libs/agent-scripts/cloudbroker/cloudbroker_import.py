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
    import tarfile
    import subprocess
    from CloudscalerLibcloud import openvstorage

    try:
        pr = subprocess.Popen(['curl', '%s/%s' % (link.rstrip('/'), path.lstrip('/')), '--user', '%s:%s' % (username, passwd)], stdout=subprocess.PIPE)
        with tarfile.open(mode='r|*', fileobj=pr.stdout) as tf:
            with openvstorage.TempStorage() as ts:
                disks = [disk['path'] for disk in machine['disks']]
                for member in tf:
                    if member.name in disks:
                        ind = disks.index(member.name)
                        disk = machine['disks'][ind]
                        if member.name == disks[0]:
                            isdata = False
                            path = "vm-%d/bootdisk-vm-%d.raw" % (machine['id'], machine['id'])
                        else:
                            isdata = True
                            path = "volumes/volume_%d.raw" % (disk['id'])
                        tf.extract(member, ts.path)
                        disk['guid'], disk['path'] = openvstorage.importVolume('%s/%s' % (ts.path, member.name), path, isdata)
                        j.system.fs.remove('%s/%s' % (ts.path, member.name))
        return machine

    finally:
        pr.wait()


if __name__ == "__main__":
    print(action('http://192.168.27.152/owncloud/remote.php/webdav', 'myuser', 'rooter', '/images/mie.tar.gz', {
        'id': 5555,
        'disks': [{
            'id': '6666',
            'path': 'disk-0.vmdk'
        }]
    }))
