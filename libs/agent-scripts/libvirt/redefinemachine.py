from JumpScale import j

descr = """
Libvirt script to redefine a machine
"""

name = "redefinemachine"
category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'hypervisor'


def action(xml, domainid):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    domain = connection._get_domain(domainid)
    if domain:
        domain.undefineFlags(0)
        domain = connection.connection.defineXML(xml)
    return True
