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


def action(vm_id, sourceurl, domainxml, force, vmlog_dir, netinfo):
    import libvirt
    from xml.etree import ElementTree
    from urlparse import urlparse
    from CloudscalerLibcloud.utils.network import NetworkTool
    j.system.fs.createDir(vmlog_dir)
    try:
        source_con = libvirt.open(sourceurl)
    except:
        # source machine is not available
        source_con = None

    with NetworkTool(netinfo):
        if source_con:
            parsedsourceurl = urlparse(sourceurl)
            localip = j.system.net.getReachableIpAddress(parsedsourceurl.hostname, 22)
            target_con = libvirt.open(sourceurl.replace(parsedsourceurl.hostname, localip))  # local
            targeturl = "tcp://{}".format(localip)
            try:
                domain = source_con.lookupByUUIDString(vm_id)
            except libvirt.libvirtError as e:
                if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                    return -1 # nothing to do domain is not running
                raise

            if domain.state()[0] in (libvirt.VIR_DOMAIN_RUNNING, libvirt.VIR_DOMAIN_PAUSED):
                srcdom = ElementTree.fromstring(domain.XMLDesc(libvirt.VIR_DOMAIN_XML_MIGRATABLE))
                seclabel = srcdom.find('seclabel')
                if seclabel is not None:
                    srcdom.remove(seclabel)
                flags = libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_UNDEFINE_SOURCE | \
                        libvirt.VIR_MIGRATE_PEER2PEER
                try:
                    domain.migrate2(target_con, flags=flags, dxml=ElementTree.tostring(srcdom), uri=targeturl)
                    return 0
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
            target_con = libvirt.open()  # local
            target_con.createXML(domainxml)
    return 1

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--vmid')
    parser.add_argument('--sourceurl')
    options = parser.parse_args()
    action(options.vmid, options.sourceurl, '', False)
