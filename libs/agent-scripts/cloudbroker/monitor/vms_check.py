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

    REDIS_PORT = j.application.config.get('redis.port.redisp')
    WHERE_AM_I = j.application.config.get('cloudbroker.where.am.i')

    rediscl = j.clients.redis.getGeventRedisClient('127.0.0.1', REDIS_PORT)
    accl = j.clients.agentcontroller.get()
    osiscl = j.core.osis.getClient(user='root')
    cbcl = j.core.osis.getClientForNamespace('cloudbroker')
    nodecl = j.core.osis.getClientForCategory(osiscl, 'system', 'node')

    # get all stacks and nodes data, save trips to osis
    stacks = dict([(s['id'], s) for s in cbcl.stack.simpleSearch({})])
    nodes = dict([(n['name'], n) for n in nodecl.simpleSearch({})])

    cloudspaces = cbcl.cloudspace.simpleSearch({'location': WHERE_AM_I})

    for cloudspace in cloudspaces:
        vms = cbcl.vmachine.simpleSearch({'cloudspaceId': cloudspace['id']})
        for vm in vms:
            cpu_node_name = stacks[vm['stackId']]['referenceId']
            cpu_node_id = nodes[cpu_node_name]['id']
            vm_data = {'state': vm['status'], 'ping': False, 'hdtest': False, 'cpu_node_name': cpu_node_name,
                       'cpu_node_id': cpu_node_id, 'epoch': j.base.time.getTimeEpoch()}
            if vm['status'] == 'RUNNING':
                args = {'vm_ip_address': vm['nics'][0]['ipAddress'], 'vm_cloudspace_id': cloudspace['id']}
                result = accl.executeJumpScript('jumpscale', 'vm_ping', role='admin', args=args, wait=True)
                if result['state'] == 'OK':
                    result = result['result']
                    vm_data['ping'] = result

            result = accl.executeJumpScript('jumpscale', 'vm_disk_check', nid=cpu_node_id, args={'vm_id': vm['id']}, wait=True)
            if result['state'] == 'OK':
                result = result['result']
                vm_data['hdtest'] = True
                vm_data['image'] = result['image']
                vm_data['parent_image'] = result['backing file']
                vm_data['disk_size'] = result['disk size']

            rediscl.hset('vmachines.status', vm['id'], vm_data)
