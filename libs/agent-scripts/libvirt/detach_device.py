from JumpScale import j

descr = """
Libvirt script to ge the domain
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(xml, machineid):
    import libvirt
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    try:
        domain = connection.connection.lookupByUUIDString(machineid)
    except:
        return None  # machine not available anymore
    flags = 0
    if domain.state()[0] in (libvirt.VIR_DOMAIN_RUNNING, libvirt.VIR_DOMAIN_PAUSED):
        flags |= libvirt.VIR_DOMAIN_DEVICE_MODIFY_LIVE
    if domain.isPersistent():
        flags |= libvirt.VIR_DOMAIN_DEVICE_MODIFY_CONFIG
    if flags != 0:
        domain.detachDeviceFlags(xml, flags)
    return domain.XMLDesc()



