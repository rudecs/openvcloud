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

def action(gid=None):
    import JumpScale.grid.osis
    import JumpScale.lib.routeros
    import JumpScale.baselib.redis
    import JumpScale.grid.agentcontroller
    import ujson as json

    rediscl = j.clients.redis.getGeventRedisClientByInstanceName('production')
    accl = j.clients.agentcontroller.get()
    osiscl = j.core.osis.getClientByInstance('main')
    cbcl = j.core.osis.getClientForNamespace('cloudbroker')
    nodecl = j.core.osis.getClientForCategory(osiscl, 'system', 'node')

    # get all stacks and nodes data, save trips to osis
    stacks = dict([(s['id'], s) for s in cbcl.stack.search({})])
    nodes = dict([(n['id'], n) for n in nodecl.search({})])

    ping_jobs = dict()
    disk_check_jobs = dict()
    vmachines_data = dict()
    query = {}
    if gid:
        query['gid'] = gid
    cloudspaces = cbcl.cloudspace.search(query)[1:]

    for cloudspace in cloudspaces:
        gid = gid or cloudspace['gid']
        query = {'cloudspaceId': cloudspace['id'], 'status': {'$ne': 'DESTROYED'}}
        vms = cbcl.vmachine.search(query)[1:]
        for vm in vms:
            if vm['stackId'] in stacks:
                cpu_node_id = int(stacks[vm['stackId']]['referenceId'])
                cpu_node_name = nodes[cpu_node_id].get('name', 'N/A')
            else:
                cpu_node_id = 0
                cpu_node_name = 'N/A'
            vm_data = {'state': vm['status'], 'ping': False, 'hdtest': False, 'cpu_node_name': cpu_node_name,
                       'cpu_node_id': cpu_node_id, 'epoch': j.base.time.getTimeEpoch()}
            vmachines_data[vm['id']] = vm_data
            if vm['status'] == 'RUNNING':
                args = {'vm_ip_address': vm['nics'][0]['ipAddress'], 'vm_cloudspace_id': cloudspace['id']}
                job = accl.scheduleCmd(gid, cpu_node_id, 'jumpscale', 'vm_ping', args=args, queue='default', log=False, timeout=5, roles=['fw'], wait=True)
                ping_jobs[vm['id']] = job

            if vm['status']:
                job = accl.scheduleCmd(gid, cpu_node_id, 'jumpscale', 'vm_disk_check', args={'vm_id': vm['id']}, queue='default', log=False, timeout=5, wait=True)
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
            vmachines_data[vm_id]['image'] = result.get('image', 'N/A')
            vmachines_data[vm_id]['parent_image'] = result.get('backing file', 'N/A')
            vmachines_data[vm_id]['disk_size'] = result.get('disk size', 'N/A')

    for vm_id, vm_data in vmachines_data.iteritems():
        rediscl.hset('vmachines.status', vm_id, json.dumps(vm_data))
    return vmachines_data
