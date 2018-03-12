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
    destination = '/var/lib/libvirt/images/routeros/{0:04x}/routeros.qcow2'.format(networkid)
    try:
        network_id_hex = '%04x' % int(networkid)
        name = 'routeros_%s' % network_id_hex
        try:
            domain = con.lookupByName(name)
            if domain:
                network.cleanup_gwmgmt(domain)
                network.cleanup_external(domain)
                domain.shutdown()
                domain.undefine()
                j.system.fs.remove(destination)
                return True
            else:
                return True
        except libvirt.libvirtError:
            return False
    finally:
        con.close()


