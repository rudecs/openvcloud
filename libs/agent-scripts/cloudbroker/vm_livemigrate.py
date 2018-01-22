from JumpScale import j  # NOQA

descr = """
Prepares a live-migration action for a vm by creating disks
"""

name = "vm_livemigrate"
category = "cloudbroker"
organization = "greenitglobe"
author = "deboeckj@codescalers.com, muhamad.azmy@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"
async = True


def action(vm_id, sourceurl, domainxml, force):
    import libvirt
    from urlparse import urlparse
    target_con = libvirt.open()  # local
    try:
        source_con = libvirt.open(sourceurl)
    except:
        # source machine is not available
        source_con = None

    if source_con:
        parsedsourceurl = urlparse(sourceurl)
        localip = j.system.net.getReachableIpAddress(parsedsourceurl.hostname, 22)
        targeturl = "tcp://{}".format(localip)
        domain = source_con.lookupByUUIDString(vm_id)

        if domain.state()[0] in (libvirt.VIR_DOMAIN_RUNNING, libvirt.VIR_DOMAIN_PAUSED):
            flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE
            try:
                domain.migrate2(target_con, flags=flags, uri=targeturl)
            except:
                if force:
                    try:
                        domain.destroy()
                    except Exception as e:
                        j.errorconditionhandler.processPythonExceptionObject(e)
                    target_con.createXML(domainxml)
                else:
                    raise

        else:
            domain.undefine()
            target_con.createXML(domainxml)
    else:
        target_con.createXML(domainxml)
    return True
