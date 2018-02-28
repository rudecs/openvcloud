import time
from JumpScale import j


descr = """
Permanently removes machines with status deleted if the configured period for this grid has passed since deletion. (Empties the trash can)
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "chaddada@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['master']
queue = "hypervisor"
async = True
log = True
enable = True
period = 3600

def action():
    from CloudscalerLibcloud.utils.gridconfig import GridConfig
    ccl = j.clients.osis.getNamespace('cloudbroker')
    current_time = time.time()
    machines = ccl.vmachine.search({'status': 'DELETED'}, size=0)[1:]
    acl = j.clients.agentcontroller.get()
    scl = j.clients.osis.getNamespace('system')
    grid_info = {}
    for machine in machines:
        deletion_time = machine['deletionTime']
        cloudspace = ccl.cloudspace.get(machine['cloudspaceId'])
        grid_id = cloudspace.gid
        grid = scl.grid.get(grid_id)
        grid_config = GridConfig(grid)
        retention_period = grid_config.get('delete_retention_period')
        if current_time >= (deletion_time + retention_period):
            ccl.vmachine.updateSearch({'id': machine['id']}, {'$set': {'status': 'DESTROYED'}})
            query = {'id': {'$in': machine['disks']}}
            if not grid_id in grid_info:
                ovs_cred = grid_config.settings['ovs_credentials']
                ovs_connection = {'ips': ovs_cred['ips'],
                                  'client_id': ovs_cred['client_id'],
                                  'client_secret': ovs_cred['client_secret']}
                grid_info[grid_id] = {'ovs_connection': ovs_connection, 'diskguids': []}
            for disk in ccl.disk.search(query)[1:]:
                diskguid = disk['referenceId'].split('@')[1]
                grid_info[grid_id]['diskguids'].append(diskguid)
            ccl.disk.updateSearch(query, {'$set': {'status': 'DESTROYED'}})
    for gid, grid in grid_info.items():
        args = {'diskguids': grid['diskguids'], 'ovs_connection': grid['ovs_connection']}
        acl.executeJumpscript(organization='greenitglobe', name='deletedisks', role='storagedriver', gid=gid, args=args)


if __name__ == '__main__':
    action()
