from JumpScale import j

descr = """
get the envelope of an ova
"""

category = "cloudbroker"
organization = "greenitglobe"
author = "elawadim@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
queue = 'io'
async = True
timeout = 60 * 60


def action(link, username, passwd, path):
    import requests
    import tarfile

    r = requests.get('%s/%s' % (link.rstrip('/'), path.lstrip('/')), stream=True, auth=(username, passwd))
    tf = tarfile.open(mode='r|*', fileobj=r.raw)
    for member in tf:
        if member.name.endswith('.ovf'):
            return tf.extractfile(member).read()
    return None

if __name__ == "__main__":
    print(action('http://192.168.27.152/owncloud/remote.php/webdav', 'myuser', 'rooter', '/images/mie.tar.gz'))
