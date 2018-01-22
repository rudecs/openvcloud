from JumpScale import j

descr = """
create and start a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
enable = True
async = True
queue = 'hypervisor'

def action(networkid):
    import libvirt
    from CloudscalerLibcloud.utils.network import Network
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    libvirtutil = LibvirtUtil()
    network = Network(libvirtutil)

    con = libvirtutil.connection
    try:
        networkidHex = '%04x' % int(networkid)
        name = 'routeros_%s' % networkidHex
        try:
            domain = con.lookupByName(name)
            network.cleanup_gwmgmt(domain)
            network.cleanup_external(domain)
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                domain.shutdown()
                return True
            else:
                return True
        except libvirt.libvirtError:
            return False
    finally:
        con.close()


