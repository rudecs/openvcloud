from JumpScale import j

descr = """
Libvirt script to start all machines
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action():
    import libvirt
    con = libvirt.open()
    for dom in con.listAllDomains():
        if dom.state()[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            dom.shutdown()
    con.close()
    return True


if __name__ == '__main__':
    action()
