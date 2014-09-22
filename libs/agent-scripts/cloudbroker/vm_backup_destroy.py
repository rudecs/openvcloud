from JumpScale import j

descr = """
Backup a VM and destroy it
"""

name = "vm_backup_destroy"
category = "cloudbroker"
organization = "cloudscalers"
author = "khamisr@codescalers.com"
icense = "bsd"
version = "1.0"
roles = ['compute']
queue = "hypervisor"



def action(jobguid, ticketid, accountName, cloudspaceName, machineId, reason):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import JumpScale.portal
    import JumpScale.lib.whmcs
    import time

    agentcontrollerclient = j.clients.agentcontroller.get()
    while True:
        job = agentcontrollerclient.getJobInfo(jobguid)
        if job['state'] in ['OK', 'ERROR']:
            break
        time.sleep(3)

    if job['state'] == 'ERROR':
        j.tools.whmcs.tickets.add_note(ticketid, 'Job backup could not be completed and will not be destroyed')
        return False

    backupid = job['result']
    j.tools.whmcs.tickets.add_note(ticketid, 'Storage ID is %s' %  backupid)


    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9999))
    secret = portalcfg.get('secret')
    cl = j.core.portal.getClient('127.0.0.1', port, secret)
    cloudbrokermachine = cl.getActor('cloudbroker','machine')

    cloudbrokermachine.destroy(accountName, cloudspaceName, machineId, reason)
    j.tools.whmcs.tickets.close_ticket(ticketid)
    return True
    
