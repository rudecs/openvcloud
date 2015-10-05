from JumpScale import j  # NOQA

descr = """
Prepares a live-migration action for a vm by creating disks
"""

name = "vm_livemigrate"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com, muhamad.azmy@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"
async = True


def action(vm_id, source_stack):
    import libvirt
    target_con = libvirt.open()  # local
    source_con = libvirt.open(source_stack['apiUrl'])

    domain = source_con.lookupByName('vm-%s' % vm_id)
    target_con.defineXML(domain.XMLDesc())

    if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
        flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE
        try:
            domain.migrate2(target_con, flags=flags)
        except:
            try:
                target_domain = target_con.lookupByName('vm-%s' % vm_id)
                target_domain.undefine()
            except:
                pass  # vm wasnt created on target
            raise
    else:
        domain.undefine()
