from JumpScale import j

descr = """
Monitor vmachines
"""

organization = 'jumpscale'
name = 'vms_monitoring'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

period = 3600 * 4 # 4 hrs 
enable = True
async = True
roles = ['admin',]
log = False
queue = 'hypervisor'

def action():
    import JumpScale.grid.osis
    import JumpScale.lib.routeros
    import JumpScale.baselib.mailclient

    osiscl = j.core.osis.getClient(user='root')
    vmcl = j.core.osis.getClientForCategory(osiscl, 'cloudbroker', 'vmachine')
    vfwcl = j.core.osis.getClientForCategory(osiscl, 'vfw', 'virtualfirewall')

    routeros_password = j.application.config.get('vfw.admin.passwd')

    running_vms = vmcl.simpleSearch({'status': 'RUNNING'})

    failed_machines = list()
    not_reachable_vfws = list()
    for vm in running_vms:
        vfws = vfwcl.simpleSearch({'domain': str(vm['cloudspaceId'])})
        if vfws:
            vfw = vfws[0]
            # validate routeros is reachable
            try:
                routeros = j.clients.routeros.get(vfw['internalip'], 'vscalers', routeros_password)
            except:
                not_reachable_vfws.append(vfw)
                continue
            if j.basetype.ipaddress.check(vm['nics'][0]['ipAddress']):
                pingable = routeros.ping(vm['nics'][0]['ipAddress'])
                if not pingable:
                    failed_machines.append(vm)
            else:
                failed_machines.append(vm)
        else:
            # cloudspace has no vfw
            j.events.bug_warning('Cloudspace does NOT have a VFW. id: "%s"' % vm['cloudspaceId'])

    if failed_machines or not_reachable_vfws:
        # raise to ops
        message = 'Hello,'
        if failed_machines:
            message += '<br/><br/>The following VMachines are not pingable:<br/><br/>'
            for vm in failed_machines:
                message += '* %s: %s<br/>' % (vm['id'], vm['name'])
        if not_reachable_vfws:
            message += '<br/><br/>The following VFWs are not reachable:<br/><br/>'
            for vfw in not_reachable_vfws:
                message += '* %s: %s, %s<br/>' % (vfw['name'], vfw['internalip'], ', '.join(vfw['pubips']))

        j.clients.email.send('support@mothership1.com', 'monitoring@mothership1.com', 'VMachines Status', message)
