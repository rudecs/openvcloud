import xml.etree.cElementTree as xml
import urlparse
import os
import re
import requests
from collections import namedtuple

File = namedtuple('File', ['name', 'size', 'mtime', 'ctime', 'contenttype'])


def prop(elem, name, default=None):
    child = elem.find('.//{DAV:}' + name)
    return default if child is None else child.text


def elem2file(elem):
    contenttype = prop(elem, 'getcontenttype', ''),
    name = prop(elem, 'href')
    if name.endswith('/'):
        contenttype = ('directory',)
    name = os.path.basename(name.strip('/'))
    return File(
        name,
        int(prop(elem, 'getcontentlength', 0)),
        prop(elem, 'getlastmodified', ''),
        prop(elem, 'creationdate', ''),
        contenttype
    )


def join(p1, p2):
    if not p1.endswith('/'):
        p1 += '/'
    return urlparse.urljoin(p1, p2.strip('/'))


class WebDav(object):
    def __init__(self, baseurl, username, password):
        self._baseurl = baseurl
        self.session = requests.Session()
        self.session.auth = (username, password)

    def list(self, path='/'):
        url = join(self._baseurl, path)
        res = self.session.request('propfind', url)
        if res.status_code > 300:
            raise RuntimeError("Failed to list {}:{}".format(res.status_code, res.text))
        tree = xml.fromstring(res.content)
        return [elem2file(elem) for elem in tree.findall('{DAV:}response')]

    def get(self, path='/', stream=True):
        url = join(self._baseurl, path)
        return self.session.get(url, stream=stream)

    def put(self, path='/', data=None):
        url = join(self._baseurl, path)
        return self.session.put(url, data=data)


def find_ova_files(webdavcon, path='/'):
    rec = re.compile('^.*\.ova\.gz\.\d{9}$')
    files = sorted(webdavcon.list(path))
    ovafiles = []
    for fileobj in files:
        if 'directory' in fileobj.contenttype:
            continue
        filename = fileobj.name
        if filename == '.ova':
            return [filename]
        elif filename == '.ova.gz':
            return [filename]
        elif rec.match(filename):
            ovafiles.append(filename)
    return ovafiles
