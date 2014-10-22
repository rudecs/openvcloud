from JumpScale import j

descr = """
Check vmachines status
"""

organization = 'jumpscale'
name = 'vms_check'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

period = 3600 * 2 # 2 hrs 
enable = True
async = True
roles = ['master',]
log = False

def action():
    import JumpScale.grid.osis
    import JumpScale.lib.routeros
    import JumpScale.baselib.redis
    import JumpScale.grid.agentcontroller
    import ujson as json

    rediscl = j.clients.redis.getGeventRedisClientByInstanceName('production')
    accl = j.clients.agentcontroller.get()
    osiscl = j.core.osis.getClient(user='root')
    cbcl = j.core.osis.getClientForNamespace('cloudbroker')
    nodecl = j.core.osis.getClientForCategory(osiscl, 'system', 'node')

    # get all stacks and nodes data, save trips to osis
    stacks = dict([(s['id'], s) for s in cbcl.stack.simpleSearch({})])
    nodes = dict([(n['name'], n) for n in nodecl.simpleSearch({})])

    ping_jobs = dict()
    disk_check_jobs = dict()
    vmachines_data = dict()
    cloudspaces = cbcl.cloudspace.simpleSearch({'location': WHERE_AM_I})

    for cloudspace in cloudspaces:
        query = {'query': {'bool': {'must_not': {'term': {'status': 'destroyed'}}, 'must': {'term': {'cloudspaceId': cloudspace['id']}}}}}
        vms = cbcl.vmachine.simpleSearch({}, nativequery=query)
        for vm in vms:
            if vm['stackId'] in stacks:
                cpu_node_name = stacks[vm['stackId']]['referenceId']
                cpu_node_id = nodes[cpu_node_name]['id']
            else:
                cpu_node_id = 0
                cpu_node_name = 'N/A'
            vm_data = {'state': vm['status'], 'ping': False, 'hdtest': False, 'cpu_node_name': cpu_node_name,
                       'cpu_node_id': cpu_node_id, 'epoch': j.base.time.getTimeEpoch()}
            vmachines_data[vm['id']] = vm_data
            if vm['status'] == 'RUNNING':
                args = {'vm_ip_address': vm['nics'][0]['ipAddress'], 'vm_cloudspace_id': cloudspace['id']}
                job = accl.scheduleCmd(j.application.whoAmI.gid, None, 'jumpscale', 'vm_ping', args=args, queue='default', log=False, timeout=5, roles=['admin'], wait=True)
                ping_jobs[vm['id']] = job

            if vm['status']:
                job = accl.scheduleCmd(j.application.whoAmI.gid, cpu_node_id, 'jumpscale', 'vm_disk_check', args={'vm_id': vm['id']}, queue='default', log=False, timeout=5, wait=True)
                disk_check_jobs[vm['id']] = job

    for vm_id, job in ping_jobs.iteritems():
        result = accl.waitJumpscript(job=job)
        if result['result']:
            vmachines_data[vm_id]['ping'] = result['result']

    for vm_id, job in disk_check_jobs.iteritems():
        result = accl.waitJumpscript(job=job)
        if result['result']:
            result = result['result']
            vmachines_data[vm_id]['hdtest'] = True
            vmachines_data[vm_id]['image'] = result['image']
            vmachines_data[vm_id]['parent_image'] = result['backing file']
            vmachines_data[vm_id]['disk_size'] = result['disk size']

    for vm_id, vm_data in vmachines_data.iteritems():
        rediscl.hset('vmachines.status', vm_id, json.dumps(vm_data))
    return vmachines_data
