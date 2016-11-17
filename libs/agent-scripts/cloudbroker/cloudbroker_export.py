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
    from CloudscalerLibcloud import openvstorage

    def reset(tarinfo):
        tarinfo.name = os.path.basename(tarinfo.name)
        return tarinfo

    with openvstorage.TempStorage() as ts:
        tarpath = os.path.join(ts.path, 'export.ova')
        with tarfile.open(tarpath, 'w') as tar:
            ti = tarfile.TarInfo('descriptor.ovf')
            ti.size = len(envelope)
            tar.addfile(ti, BytesIO(j.tools.text.toStr(envelope)))
            j.system.fs.writeFile(filename=os.path.join(ts.path, 'descriptor.ovf'), contents=envelope)
            tmpvolname = 'disk-%i.vmdk'
            for i, disk in enumerate(disks):
                print('Converting %s' % disk)
                vmdk = os.path.join(ts.path, tmpvolname % i)
                openvstorage.exportVolume(disk, vmdk)
                tar.add(vmdk, filter=reset)
        print('Uploading tar')
        with open(tarpath, 'rb') as tar:
            res = requests.put(os.path.join(link, path.strip('/')), data=tar, auth=(username, passwd))
            if res.status_code >= 300:
                raise RuntimeError("Failed to upload error %s" % res.text)


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
