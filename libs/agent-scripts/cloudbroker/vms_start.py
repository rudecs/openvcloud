from JumpScale import j

descr = """
Start all machines in the grid which are indicated to start
"""

name = "vms_start"
category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['cloudbroker']
queue = "hypervisor"
async = True

def action():
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    ccl = j.core.osis.getClientForNamespace('cloudbroker')
    stacks = { x['id']: x for x in ccl.stacks.simpleSearch({}) }
    acl = j.clients.agentcontroller.get()
    failedvms = list()
    whereami = j.application.config.get('cloudbroker.where.am.i')
    for cloudspace in ccl.cloudspace.simpleSearch({'location': whereami}):
        for vm in ccl.vmachine.simpleSearch({'cloudspaceId': cloudspace['id']}):
            name = 'vm-%s' % vm['id']
            role = stacks[vm['stackId']]['referenceId']
            try:
                if vm['status'] == 'RUNNING':
                    args = {'name': name, 'networkId': cloudspace['networkId']}
                    acl.executeJumpscript('cloudscalers', 'vm_start', role=role, args=args, wait=False)
            except Exception, e:
                failedvms.append((name, e))
    if failedvms:
        errormsg = "Some machines failed to try to start bad model\n"
        for name, msg in failedvms:
            errormsg += "* %s: %s" % name, msg

        raise RuntimeError(errormsg)


