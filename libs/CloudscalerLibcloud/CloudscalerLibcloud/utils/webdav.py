import tarfile

import requests


def upload_file(link, username, passwd, path, file_location):
    with open(file_location, 'rb') as f:
        requests.put('%s/%s' % (link.rstrip('/'), path.lstrip('/')), data=f, auth=(username, passwd))


def download_file(link, username, passwd, path, file_location):
    r = requests.get('%s/%s' % (link.rstrip('/'), path.lstrip('/')), stream=True, auth=(username, passwd))
    with open(file_location, 'wb') as f:
        for chunk in r.iter_content(4096):
            f.write(chunk)


def get_tar_first_file(link, username, passwd, path):
    r = requests.get('%s/%s' % (link.rstrip('/'), path.lstrip('/')), stream=True, auth=(username, passwd))
    tf = tarfile.open(mode='r|*', fileobj=r.raw)
    for member in tf:
        if member.name.endswith('.ovf'):
            return tf.extractfile(member).read()
    return None
