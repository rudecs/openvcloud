from JumpScale import j
import time

descr = """
Check vmachines status
"""

organization = 'jumpscale'
name = 'vms_check'
author = "zains@codescalers.com"
version = "1.0"
category = "monitor.vms"

period = 3600 * 2 # 2 hrs
enable = False
async = True
roles = ['master',]
log = False

def action(gid=None):
    import JumpScale.grid.osis
    import JumpScale.portal
    import JumpScale.lib.routeros
    import JumpScale.baselib.redis
    import JumpScale.grid.agentcontroller
    import ujson as json

    rediscl = j.clients.redis.getByInstance('system')
    accl = j.clients.agentcontroller.get()
    osiscl = j.clients.osis.getByInstance('main')
    cbcl = j.clients.osis.getNamespace('cloudbroker')
    vcl = j.clients.osis.getNamespace('vfw')
    portalclient = j.clients.portal.getByInstance('cloudbroker').actors
    nodecl = j.clients.osis.getCategory(osiscl, 'system', 'node')

    # get all stacks and nodes data, save trips to osis
    stacks = dict([(s['id'], s) for s in cbcl.stack.search({})[1:]])
    nodes = dict([(n['id'], n) for n in nodecl.search({})[1:]])

    ping_jobs = dict()
    disk_check_jobs = dict()
    vmachines_data = dict()
    query = {'status': {'$ne': 'DESTROYED'}}
    if gid:
        query['gid'] = gid
    cloudspaces = cbcl.cloudspace.search(query)[1:]

    for cloudspace in cloudspaces:
        gid = cloudspace['gid']
        print 'Cloudspace %(accountId)s %(name)s' % cloudspace
        query = {'cloudspaceId': cloudspace['id'], 'status': {'$nin': ['ERROR', 'DESTROYED']}}
        vms = cbcl.vmachine.search(query)[1:]
        vfwid = '%(gid)s_%(networkId)s' % cloudspace
        if cloudspace['status'] == 'DEPLOYED' and vcl.virtualfirewall.exists(vfwid):
            vfw = vcl.virtualfirewall.get(vfwid)
        else:
            vfw = None
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
                ipaddress = vm['nics'][0]['ipAddress']
                if ipaddress == 'Undefined':
                    print 'Retreiving vm from portal %(id)s' % vm
                    vmdata = portalclient.cloudapi.machines.get(vm['id'])
                    ipaddress = vmdata['interfaces'][0]['ipAddress']
                if ipaddress != 'Undefined' and vfw:
                    args = {'vm_ip_address': ipaddress, 'vm_cloudspace_id': cloudspace['id']}
                    job = accl.scheduleCmd(vfw.gid, vfw.nid, 'jumpscale', 'vm_ping', args=args, queue='default', log=False, timeout=5, wait=True)
                    ping_jobs[vm['id']] = job

            if vm['status'] and cpu_node_id:
                diskpaths = [ disk['referenceId'] for disk in cbcl.disk.search({'id': {'$in': vm['disks']}})[1:] ]
                job = accl.scheduleCmd(gid, cpu_node_id, 'jumpscale', 'vm_disk_check', args={'diskpaths': diskpaths}, queue='default', log=False, timeout=5, wait=True)
                disk_check_jobs[vm['id']] = job
    time.sleep(5)
    for idx, (vm_id, job) in enumerate(ping_jobs.iteritems()):
        print 'Waiting for %s/%s pingjobs' % (idx + 1, len(ping_jobs))
        result = accl.waitJumpscript(job=job, timeout=0)
        if result['state'] != 'OK':
            vmachines_data[vm_id]['ping'] = False
        elif isinstance(result['result'], bool):
            vmachines_data[vm_id]['ping'] = result['result']

    for idx, (vm_id, job) in enumerate(disk_check_jobs.iteritems()):
        print 'Waiting for %s/%s disk_check_jobs' % (idx + 1, len(disk_check_jobs))
        result = accl.waitJumpscript(job=job, timeout=0)
        if result['state'] == 'OK' and result['result']:
            result = result['result']
            vmachines_data[vm_id]['diskinfo'] = result
            vmachines_data[vm_id]['hdtest'] = True

    for vm_id, vm_data in vmachines_data.iteritems():
        rediscl.hset('vmachines.status', vm_id, json.dumps(vm_data))
    return vmachines_data


if __name__ == '__main__':
    action()
