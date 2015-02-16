from JumpScale import j

descr = """
Checks vmachine disk(s)
"""

organization = 'jumpscale'
name = 'vm_disk_check'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

enable = True
async = True
log = False

def action(vm_id):
    import JumpScale.lib.qemu_img
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    lv = LibvirtUtil()
    vm = lv.connection.lookupByName('vm-%s' % vm_id)

    DISK_PATH = lv._getDomainDiskFiles(vm)[0]

    return j.system.platform.qemu_img.info(DISK_PATH)