from JumpScale import j

descr = """
Cleanup network config
"""

organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "cleanup.network"
enable = True
async = True

def action(networkid, domainxml=None):
    from CloudscalerLibcloud.utils.network import Network
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    j.system.ovsnetconfig.cleanupIfUnused(networkid)
    if domainxml:
        libvirtutil = LibvirtUtil()
        network = Network(libvirtutil)
        network.cleanup_gwmgmt(domainxml)
        network.cleanup_external(domainxml)
        destination = '/var/lib/libvirt/images/routeros/{0:04x}/'.format(networkid)
        j.system.fs.removeDirTree(destination)


