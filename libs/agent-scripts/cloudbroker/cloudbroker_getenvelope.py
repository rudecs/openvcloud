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
    import tarfile
    from CloudscalerLibcloud.utils.webdav import WebDav, join, find_ova_files

    url = join(link, path)
    connection = WebDav(url, username, passwd)
    ovafiles = find_ova_files(connection)
    if not ovafiles:
        raise RuntimeError("Could not find envelope")
    r = connection.get(ovafiles[0])
    tf = tarfile.open(mode='r|*', fileobj=r.raw)
    for member in tf:
        if member.name.endswith('.ovf'):
            return tf.extractfile(member).read()
    raise RuntimeError("Could not find envelope")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', default='admin')
    parser.add_argument('-p', '--password', default='admin')
    parser.add_argument('-url', '--url')
    parser.add_argument('-path', '--path')
    options = parser.parse_args()
    action(options.url, options.user, options.password, options.path)
