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
        network_id_hex = '%04x' % int(networkid)
        name = 'routeros_%s' % network_id_hex
        try:
            domain = con.lookupByName(name)
            if domain.state()[0] in (libvirt.VIR_DOMAIN_RUNNING, libvirt.VIR_DOMAIN_PAUSED):
                network.cleanup_gwmgmt(domain)
                network.cleanup_external(domain)
                domain.shutdown()
                return True
            else:
                return True
        except libvirt.libvirtError:
            return False
    finally:
        con.close()


