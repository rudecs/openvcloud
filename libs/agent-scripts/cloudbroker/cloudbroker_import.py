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
timeout = 60 * 60 * 24


def action(link, username, passwd, path, machine):
    import tarfile
    from CloudscalerLibcloud import openvstorage
    from CloudscalerLibcloud.utils.webdav import WebDav, join, find_ova_files
    from JumpScale.core.system.streamchunker import StreamUnifier

    url = join(link, path)
    connection = WebDav(url, username, passwd)
    ovafiles = find_ova_files(connection)

    def get_ova_streams():
        for ovafile in ovafiles:
            yield connection.get(ovafile, stream=True).raw

    with openvstorage.TempStorage() as ts:
        with tarfile.open(mode='r|*', fileobj=StreamUnifier(get_ova_streams())) as tar:
            disks = [disk['file'] for disk in machine['disks']]
            for member in tar:
                print('Iterating %s' % member.name)
                if member.name in disks:
                    print('Processing %s' % member.name)
                    ind = disks.index(member.name)
                    disk = machine['disks'][ind]
                    if member.name == disks[0]:
                        isdata = False
                        path = "vm-%d/bootdisk-vm-%d.raw" % (machine['id'], machine['id'])
                    else:
                        isdata = True
                        path = "volumes/volume_%d.raw" % (disk['id'])
                    print('Extracting')
                    tar.extract(member, ts.path)
                    print('Converting')
                    disk['guid'], disk['path'] = openvstorage.importVolume(
                        '%s/%s' % (ts.path, member.name), path, isdata)
                    j.system.fs.remove('%s/%s' % (ts.path, member.name))
    return machine


if __name__ == "__main__":
    print(action('http://192.168.27.152/owncloud/remote.php/webdav', 'myuser', 'rooter', '/images/mie.tar.gz', {
        'id': 5555,
        'disks': [{
            'id': '6666',
            'path': 'disk-0.vmdk'
        }]
    }))
