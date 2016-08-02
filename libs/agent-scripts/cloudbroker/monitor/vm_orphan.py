from JumpScale import j

descr = """
Checks if libvirt still has VMs that are not known by the system. These VM's are called Orphan VMs.
Takes into account VMs that have been moved to other CPU Nodes.

If Orphan disks exist, WARNING is shown in the healthcheck space.

"""

organization = 'jumpscale'
category = "monitor.healthcheck"
name = 'vm_orphan'
author = "deboeckj@codescalers.com"
version = "1.0"

period = 3600 # 1 hrs
enable = True
async = True
roles = ['cpunode',]
queue = 'process'

def action():
    import libvirt
    result = []
    cbcl = j.clients.osis.getNamespace('cloudbroker', j.core.osis.client)
    vcl = j.clients.osis.getNamespace('vfw', j.core.osis.client)
    stacks = cbcl.stack.search({'gid': j.application.whoAmI.gid, 'referenceId': str(j.application.whoAmI.nid)})[1:]
    vfws = vcl.virtualfirewall.search({'gid': j.application.whoAmI.gid, 'nid': j.application.whoAmI.nid})[1:]
    networkids = {vfw['id'] for vfw in vfws}
    if not stacks:
        return result  # not registered as a stack
    vms = cbcl.vmachine.search({'stackId': stacks[0]['id'], 'status': {'$ne': 'DESTROYED'}})[1:]
    vmsbyguid = { vm['referenceId']: vm for vm in vms }
    con = libvirt.open()
    networkorphan = "Found orphan network %s"
    networkwrongloc = "Found network %s which should be at node %s"
    vmorphan = "Found orphan %s"
    vmwrongloc = "Found %s which should be at stack %s"
    messages = []
    try:
        domains = con.listAllDomains()
        for domain in domains:
            name = domain.name()
            if name.startswith('routeros'):
                networkid = int(name.split('_')[-1], 16)
                if networkid not in networkids:
                    vfw = next(iter(vcl.virtualfirewall.search({"id": networkid})[1:]), None)
                    if vfw:
                        messages.append(networkwrongloc % (networkid, vfw['nid']))
                    else:
                        messages.append(networkorphan % networkid)
            elif domain.UUIDString() not in vmsbyguid:
                vm = next(iter(cbcl.vmachine.search({"referenceId": domain.UUIDString()})[1:]), None)
                if vm:
                    messages.append(vmwrongloc % (domain.name(), vm['stackId']))
                else:
                    messages.append(vmorphan % (domain.name()))
    finally:
        con.close()

    if messages:
        for message in messages:
            result.append({'state': 'WARNING', 'category': 'Orphanage', 'message': message, 'uid': message})
        errormsg = '\n'.join(messages)
        print(errormsg)
        j.errorconditionhandler.raiseOperationalWarning(errormsg, 'monitoring')
    else:
        result.append({'state': 'OK', 'category': 'Orphanage', 'message': 'No orphans found'})

    return result

if __name__ == '__main__':
    import yaml
    j.core.osis.client = j.clients.osis.getByInstance('main')
    print yaml.dump(action(), default_flow_style=False)
