from JumpScale import j

descr = """
Libvirt script to change vcpus
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = []
async = True


def action(machineid, vcpus):
    import libvirt
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    try:
        domain = connection.get_domain_obj(machineid)
        if domain is None:
            return
        try:
            domain.setVcpus(vcpus)
        except libvirt.libvirtError as e:
            if e.get_error_code() == 8:
                return False
            raise
        return True
    finally:
        connection.close()
