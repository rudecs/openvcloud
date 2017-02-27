from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "stopmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, force=False):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from CloudscalerLibcloud.utils.network import Network
    connection = LibvirtUtil()
    network = Network(connection)
    domain = connection.get_domain_obj(machineid)
    if domain:
        network.cleanup_external(domain)
    return connection.shutdown(machineid, force)
