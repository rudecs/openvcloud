from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_export"
category = "cloudbroker"
organization = "greenitglobe"
author = "elawadim@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
queue = 'io'
async = True
timeout = 60 * 60


def action(link, username, passwd, path, envelope, disks):
    from io import BytesIO
    import os
    import tarfile
    import requests
    import threading
    from CloudscalerLibcloud import openvstorage
    from JumpScale.core.system.streamchunker import StreamChunker
    basepath = os.path.join(link, path.strip('/'))
    blocksize = 1024 * 1024

    def upload(rfd):
        for idx, chunk in enumerate(StreamChunker(os.fdopen(rfd), chunksize=100 * 1024 ** 2)):
            print('Adding chunk', idx)
            url = '{}/export.ova.gz.{:09d}'.format(basepath, idx)
            requests.put(url, data=chunk, auth=(username, passwd))
        print('Reached end')

    def reset(tarinfo):
        tarinfo.name = os.path.basename(tarinfo.name)
        return tarinfo

    with openvstorage.TempStorage() as ts:
        vmdks = []
        tmpvolname = 'disk-%i.vmdk'
        for i, disk in enumerate(disks):
            print('Converting %s' % disk)
            vmdk = os.path.join(ts.path, tmpvolname % i)
            openvstorage.exportVolume(disk, vmdk)
            vmdks.append(vmdk)

        rfd, wfd = os.pipe()
        uploadthread = threading.Thread(target=upload, args=(rfd,))
        uploadthread.start()

        wfile = os.fdopen(wfd, 'w', blocksize)
        tar = tarfile.open(mode='w|gz', fileobj=wfile, bufsize=blocksize)

        ti = tarfile.TarInfo('descriptor.ovf')
        ti.size = len(envelope)
        tar.addfile(ti, BytesIO(j.tools.text.toStr(envelope)))
        for vmdk in vmdks:
            tar.add(vmdk, filter=reset)
        tar.close()
        wfile.close()
        uploadthread.join()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', default='admin')
    parser.add_argument('-p', '--password', default='admin')
    parser.add_argument('-d', '--disk')
    parser.add_argument('-url', '--url')
    parser.add_argument('-path', '--path')
    options = parser.parse_args()
    action(options.url, options.user, options.password, options.path, "xml", [options.disk])
