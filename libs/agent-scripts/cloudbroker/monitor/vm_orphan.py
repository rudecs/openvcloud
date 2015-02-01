from JumpScale import j

descr = """
Check for orphan vms
"""

organization = 'jumpscale'
name = 'vm_orphan'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.vm"

period = 3600 # 1 hrs 
enable = True
async = True
roles = ['cpu',]
queue = 'process'
log = False

def action():
    import libvirt
    cbcl = j.clients.osis.getForNamespace('cloudbroker', j.core.osis.client)
    stacks = cbcl.stack.search({'gid': j.application.whoAmI.gid, 'referenceId': str(j.application.whoAmI.nid)})[1:]
    if not stacks:
        return # not registered as a stack
    vms = cbcl.vmachine.search({'stackId': stacks[0]['id'], 'status': {'$ne': 'DESTROYED'}})[1:]
    vmsbyguid = { vm['referenceId']: vm for vm in vms }
    con = libvirt.open()
    orphans = list()
    try:
        domains = con.listAllDomains()
        for domain in domains:
            if domain.UUIDString() not in vmsbyguid:
                orphans.append("- %s" % domain.name())
    finally:
        con.close()

    if orphans:
        message = "Found following orphan machines\n" + "\n".join(orphans)
        print(message)
        j.errorconditionhandler.raiseOperationalWarning(message, 'monitoring')

if __name__ == '__main__':
    import JumpScale.grid.osis
    j.core.osis.client = j.clients.osis.getByInstance('main')
    action()
