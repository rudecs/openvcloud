from JumpScale import j

descr = """
Checks whether vmachine is pingable
"""

organization = 'jumpscale'
name = 'vm_ping'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

enable = False
async = True
log = False
roles = ['fw',]

def action(vm_ip_address, vm_cloudspace_id):
    import JumpScale.grid.osis
    import JumpScale.lib.routeros

    osiscl = j.clients.osis.getByInstance('main')
    vfwcl = j.clients.osis.getCategory(osiscl, 'vfw', 'virtualfirewall')

    vfws = vfwcl.simpleSearch({'domain': str(vm_cloudspace_id)})
    if vfws:
        vfw = vfws[0]
        routeros = j.clients.routeros.get(vfw['host'], 'vscalers', vfw['password'])
        pingable = routeros.ping(vm_ip_address)
        return pingable
    return False
