from JumpScale import j
import datetime
import os
import tarfile
import io
import re
import base64


descr = """
gather statistics about OVS backends
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "account.monitoring"
enable = True
async = True
queue = 'process'
log = False

roles = ['controller']


def action():
    """
    Send tar of account data on  each enviroment
    """
    base_path_active = "/opt/jumpscale7/var/resourcetracking/active"
    base_path_collected = "/opt/jumpscale7/var/resourcetracking/collected"

    def create_hour_tar():
        c = io.BytesIO()
        with tarfile.open(mode="w:gz", fileobj=c) as tar:
            tar.add(base_path_active)
        return c

    def move_to_collected(tar):
        tar.seek(0)
        with tarfile.open(mode="r:gz", fileobj=tar) as tar:
            for f in tar.getmembers():
                if f.name.endswith(".bin"):
                    accountid, year, month, day, hour, name = re.findall(
                        "opt/jumpscale7/var/resourcetracking/active/([\d]+)/([\d]+)/([\d]+)/([\d]+)/([\d]+)/([\d]+.bin)", f.name)[0]
                    try:
                        os.makedirs(os.path.join(base_path_collected, accountid, year, month, day, hour))
                    except OSError as err:
                        if err.errno != 17:
                            raise err
                    os.rename(os.path.join(base_path_active, accountid, year, month, day, hour, name),
                              os.path.join(base_path_collected, accountid, year, month, day, hour, name))
    tar = create_hour_tar()
    move_to_collected(tar)
    tar.seek(0)
    return base64.encodestring(tar.getvalue())

if __name__ == '__main__':
    action()
