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
    con = libvirt.open()
    try:
        networkidHex = '%04x' % int(networkid)
        name = 'routeros_%s' % networkidHex
        try:
            domain = con.lookupByName(name)
            if domain.state()[1] == libvirt.VIR_DOMAIN_RUNNING:
                domain.shutdown()
                return True
            else:
                return True
        except libvirt.libvirtError:
            return False
    finally:
        con.close()


