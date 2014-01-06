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
roles = ["*"]


def action(name, poolname, 	metadata, userdata):
    from CloudscalerLibcloud.utils.iso import ISO
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    pool =  connection._get_pool(poolname)
    iso = ISO()
    vol = iso.create_meta_iso(pool, name, metadata, userdata)
    return vol.name()

    
