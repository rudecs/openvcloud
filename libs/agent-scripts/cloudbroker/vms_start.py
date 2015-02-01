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
    ccl = j.clients.osis.getForNamespace('cloudbroker')
    acl = j.clients.agentcontroller.get()
    failedvms = list()
    stacks = { stack['id']: stack for stack in ccl.stack.search({})[1:] }
    for cloudspace in ccl.cloudspace.search({'status': 'DEPLOYED'})[1:]:
        for vm in ccl.vmachine.search({'cloudspaceId': cloudspace['id'], 'status': 'RUNNING'})[1:]:
            name = 'vm-%s' % vm['id']
            stack = stacks[vm['stackId']]
            nid = int(stack['referenceId'])
            gid = stacks.gid
            try:
                if vm['status'] == 'RUNNING':
                    args = {'name': name, 'networkId': cloudspace['networkId']}
                    acl.executeJumpscript('cloudscalers', 'vm_start', nid=nid, gid=gid, args=args, wait=False)
            except Exception, e:
                failedvms.append((name, e))
    if failedvms:
        errormsg = "Some machines failed to try to start bad model\n"
        for name, msg in failedvms:
            errormsg += "* %s: %s" % name, msg

        raise RuntimeError(errormsg)


