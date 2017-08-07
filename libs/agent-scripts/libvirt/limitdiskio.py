
from JumpScale import j

descr = """
Limit disk IO per seconds
"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = "hypervisor"


def action(machineid, disks, iotune):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    connection = LibvirtUtil()
    domain = connection.get_domain(machineid)
    domaindisks = list(connection.get_domain_disks(domain['XMLDesc']))

    for diskurl in disks:
        dev = connection.get_domain_disk(diskurl, domaindisks)
        if dev:
            cmd = ['virsh', 'blkdeviotune', str(machineid), str(dev)]
            for key, value in iotune.items():
                if value is not None:
                    cmd.extend(['--%s' % key, str(value)])
            cmd.extend(['--config', '--live'])
            j.system.process.execute(' '.join(cmd))

    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--vm', help='UUID of the VM')
    parser.add_argument('-d', '--disk', help='URL to disk')
    parser.add_argument('-s', '--iops', type=int, help='Disk IOPS')
    options = parser.parse_args()
    action(options.vm, [options.disk], options.iops)
