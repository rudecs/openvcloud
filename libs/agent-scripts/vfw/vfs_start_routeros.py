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
    createnetwork = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'createnetwork')
    createnetwork.executeInProcess(networkid=networkid)
    import libvirt
    con = libvirt.open()
    try:
        networkidHex = '%04x' % int(networkid)
        name = 'routeros_%s' % networkidHex
        try:
            domain = con.lookupByName(name)
            if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
                return True
            else:
                domain.create()
                return True
        except:
            return False
    finally:
        con.close()
    return True
