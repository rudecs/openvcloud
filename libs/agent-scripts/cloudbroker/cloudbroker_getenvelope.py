from JumpScale import j

descr = """
Follow up creation of export
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
    from CloudscalerLibcloud.utils import webdav
    return webdav.get_tar_first_file(link, username, passwd, path)
