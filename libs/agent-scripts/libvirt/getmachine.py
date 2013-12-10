from JumpScale import j

descr = """
Libvirt script the current status of a machine
"""

name = "getmachine"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action(machineid):
    import libvirt

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

        def get_domain(self, uuid):
            domain = self.connection.lookupByUUIDString(uuid)
            return self._to_node(domain)

        def _to_node(self, domain):
            state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
            extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time}
            return {'id': domain.UUIDString(), 'name': domain.name(), 'state':state, 'extra': extra , 'XMLDesc': domain.XMLDesc(0)} 


    connection = libvirtconn()
    return connection.get_domain(machineid)



