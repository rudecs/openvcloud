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


def action(vm_id, sourceurl, domainxml):
    import libvirt
    target_con = libvirt.open()  # local
    try:
        source_con = libvirt.open(sourceurl)
    except:
        # source machine is not available
        source_con = None

    if source_con:
        domain = source_con.lookupByUUIDString(vm_id)
        target_con.defineXML(domain.XMLDesc())

        if domain.state()[0] == libvirt.VIR_DOMAIN_RUNNING:
            flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_PERSIST_DEST | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE
            try:
                domain.migrate2(target_con, flags=flags)
            except:
                try:
                    target_domain = target_con.lookupByUUIDString(vm_id)
                    target_domain.undefine()
                except:
                    pass  # vm wasnt created on target
                raise
        else:
            domain.undefine()
    else:
        domain = target_con.defineXML(domainxml)
        domain.create()
    return True
