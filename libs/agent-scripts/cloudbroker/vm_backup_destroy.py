from JumpScale import j

descr = """
Backup a VM and destroy it
"""

name = "vm_backup_destroy"
category = "cloudbroker"
organization = "cloudscalers"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
queue = "hypervisor"



def action(accountName, machineId, reason, vmachineName, cloudspaceId):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import JumpScale.portal
#    import JumpScale.lib.whmcs
    import time

    cl = j.clients.portal.getByInstance('cbportal')

    try:
        cl.getActor('cloudbroker', 'machine')
    except Exception:
        pass
    cloudbrokermachine = cl.actors.cloudbroker.machine

    agentcontrollerclient = j.clients.agentcontroller.get()
    cbcl = j.clients.osis.getNamespace('cloudbroker')

    subject = 'Backing up Machine %s for destruction' % vmachineName
#    ticketid = j.tools.whmcs.tickets.create_ticket(subject, subject, "High")
    machineId = int(machineId)
    backupname = 'Backup of vmachine %s at %s' % (vmachineName, j.base.time.getLocalTimeHRForFilesystem())
    jobguid = cloudbrokermachine.export(machineId, backupname, backuptype='raw', storage='cephfs', host='', aws_access_key='', aws_secret_key='', bucketname='machine_backups')
    
    while True:
        job = agentcontrollerclient.getJobInfo(jobguid)
        if job['state'] in ['OK', 'ERROR']:
            break
        time.sleep(3)

    if job['state'] == 'ERROR':
#        j.tools.whmcs.tickets.add_note(ticketid, 'Job backup could not be completed and will not be destroyed')
        return False

    backupid = job['result']
#    j.tools.whmcs.tickets.add_note(ticketid, 'Storage ID is %s' %  backupid)

    cloudspace = cbcl.cloudspace.get(cloudspaceId)
    cloudbrokermachine.destroy(accountName, cloudspace.name, machineId, reason)
#    j.tools.whmcs.tickets.close_ticket(ticketid)
    return True
    
