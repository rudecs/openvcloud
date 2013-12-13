from JumpScale import j

descr = """
Libvirt script to stop a virtual machine
"""

name = "listmachines"
category = "libvirt"
organization = "cloudscalers"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = ["*"]


def action():
    import libvirt

    class libvirtconn():
        def __init__(self):
            self.connection = libvirt.open()

        def list_domains(self):
            nodes = []
            for x in self.connection.listAllDomains(0):
                nodes.append(self._to_node(x))
            return nodes

        def _to_node(self, domain):
            state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
            extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(), 'types': self.connection.getType(), 'used_memory': memory / 1024, 'vcpu_count': vcpu_count, 'used_cpu_time': used_cpu_time}
            return {'id': domain.UUIDString(), 'name': domain.name(), 'state':state, 'extra': extra} 


    connection = libvirtconn()
    return connection.list_domains()



