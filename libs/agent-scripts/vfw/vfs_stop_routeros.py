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
    bridges = []

    con = libvirtutil.connection
    destination = '/var/lib/libvirt/images/routeros/{0:04x}/routeros.qcow2'.format(networkid)
    try:
        network_id_hex = '%04x' % int(networkid)
        name = 'routeros_%s' % network_id_hex
        try:
            domain = con.lookupByName(name)
            if domain:
                bridges = list(network.libvirtutil._get_domain_bridges(domain))
                network.cleanup_gwmgmt(domain)
                network.cleanup_external(domain)
                domain.destroy()
                domain.undefine()
                j.system.fs.remove(destination)
                return True
            else:
                return True
        except libvirt.libvirtError:
            return False
    finally:
        network.libvirtutil.cleanupNetwork(networkid, bridges)
        con.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--networkid', type=int)
    options = parser.parse_args()
    action(options.networkid)


