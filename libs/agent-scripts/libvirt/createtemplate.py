from JumpScale import j

descr = """
Libvirt script to create a machine
"""

name = "createtemplate"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid, templatename, createfrom):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    return connection.exportToTemplate(machineid, templatename, createfrom)


