from JumpScale import j

descr = """
Libvirt script to create the metadata iso
"""

name = "createmetaiso"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(name, metadata, userdata, type):
    from CloudscalerLibcloud.utils.iso import ISO
    from CloudscalerLibcloud import openvstorage
    imagepath = openvstorage.getUrlPath('%s/cloud-init.%s' % (name, name))
    iso = ISO()
    iso.create_meta_iso(imagepath.replace('://', ':'), metadata, userdata, type)
    return imagepath

    
if __name__ == '__main__':
    userdata = {
        "chpasswd": {
            "expire": False
        },
        "manage_etc_hosts": True,
        "password": "FxDsKJ4kS",
        "ssh_pwauth": True,
        "users": [
            {
                "lock-passwd": False,
                "name": "cloudscalers",
                "plain_text_passwd": "FxDsKJ4kS",
                "shell": "/bin/bash",
                "sudo": "ALL=(ALL) ALL"
            }
        ]
    }
    metadata = {"local-hostname": "vm-9"}
    print action('test', metadata, userdata, 'Linux')