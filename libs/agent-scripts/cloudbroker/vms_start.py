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
    cloudspaces = { x['id']: x for x in ccl.cloudspace.simpleSearch({}) }
    acl = j.clients.agentcontroller.get()
    failedvms = list()
    for stack in ccl.stack.simpleSearch({}):
        role = stack['referenceId']
        for vm in ccl.vmachine.simpleSearch({'stackId': stack['id']}):
            name = 'vm-%s' % vm['id']
            try:
                if vm['status'] == 'RUNNING':
                    cloudspace = cloudspaces[vm['cloudspaceId']]
                    args = {'name': name, 'networkId': cloudspace['networkId']}
                    acl.executeJumpScript('cloudbroker', 'vm_start', role=role, args=args, wait=False)
            except Exception, e:
                failedvms.append((name, e))
    if failedvms:
        errormsg = "Some machines failed to try to start bad model\n"
        for name, msg in failedvms:
            errormsg += "* %s: %s" % name, msg

        raise RuntimeError(errormsg)


