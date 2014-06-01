from JumpScale import j

descr = """
Checks whether vmachine is pingable
"""

organization = 'jumpscale'
name = 'vm_ping'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

enable = True
async = True
log = False
roles = ['admin',]

def action(vm_ip_address, vm_cloudspace_id):
    import JumpScale.grid.osis
    import JumpScale.lib.routeros

    osiscl = j.core.osis.getClient(user='root')
    vfwcl = j.core.osis.getClientForCategory(osiscl, 'vfw', 'virtualfirewall')

    ROUTEROS_PASSWORD = j.application.config.get('vfw.admin.passwd')

    vfws = vfwcl.simpleSearch({'domain': str(vm_cloudspace_id)})
    if vfws:
        vfw = vfws[0]
        routeros = j.clients.routeros.get(vfw['internalip'], 'vscalers', ROUTEROS_PASSWORD)
        pingable = routeros.ping(vm_ip_address)
        return pingable
    return False