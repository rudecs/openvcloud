from JumpScale import j

descr = """
Libvirt script to ge the domain
"""

name = "attach_device"
category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(xml, machineid, ipcidr=None):
    import libvirt
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from CloudscalerLibcloud.utils.network import Network
    connection = LibvirtUtil()
    try:
        domain = connection.connection.lookupByUUIDString(machineid)
    except:
        return None  # domain does not exist
    flags = 0
    if domain.state()[0] in (libvirt.VIR_DOMAIN_RUNNING, libvirt.VIR_DOMAIN_PAUSED):
        flags |= libvirt.VIR_DOMAIN_DEVICE_MODIFY_LIVE
    if domain.isPersistent():
        flags |= libvirt.VIR_DOMAIN_DEVICE_MODIFY_CONFIG
    if flags != 0:
        domain.attachDeviceFlags(xml, flags)
    if ipcidr:
        network = Network(connection)
        network.protect_external(domain, ipcidr)
    return domain.XMLDesc()
