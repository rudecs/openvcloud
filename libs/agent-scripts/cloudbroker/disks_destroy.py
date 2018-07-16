import time
from JumpScale import j


descr = """
Permanently removes unattached disks with status 'TOBEDELETED' if the configured period for this grid has passed since deletion. (Empties the trash can)
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "ali.chaddad@gig.tech"
license = "bsd"
version = "1.0"
roles = ['master']
queue = "hypervisor"
async = True
log = True
enable = True
period = 3600
timeout = 900

def action():
    from CloudscalerLibcloud.utils.gridconfig import GridConfig
    ccl = j.clients.osis.getNamespace('cloudbroker')
    current_time = time.time()
    disks = ccl.disk.search({'status': 'TOBEDELETED'}, size=0)[1:]
    scl = j.clients.osis.getNamespace('system')
    acl = j.clients.agentcontroller.get()
    grid_info = {}
    for disk in disks:
        deletion_time = disk['deletionTime']
        grid_id = disk['gid']
        grid = scl.grid.get(grid_id)
        grid_config = GridConfig(grid)
        retention_period = grid_config.get('delete_retention_period')
        if current_time >= (deletion_time + retention_period):
            if not grid_id in grid_info:
                ovs_cred = grid_config.settings['ovs_credentials']
                ovs_connection = {'ips': ovs_cred['ips'],
                                  'client_id': ovs_cred['client_id'],
                                  'client_secret': ovs_cred['client_secret']}
                grid_info[grid_id] = {'ovs_connection': ovs_connection, 'diskguids': [], 'diskids': []}
                grid_info[grid_id]['diskids'].append(disk['id'])
                diskparts = disk['referenceId'].split('@')
                if len(diskparts) == 2:
                    grid_info[grid_id]['diskguids'].append(diskparts[1])
    for gid, grid in grid_info.items():
        args = {'diskguids': grid['diskguids'], 'ovs_connection': grid['ovs_connection']}
        acl.executeJumpscript(organization='greenitglobe', name='deletedisks', role='storagedriver', gid=gid, args=args)
        ccl.disk.updateSearch({'id': {'$in': grid['diskids']}}, {'$set': {'status': 'DESTROYED'}})




if __name__ == '__main__':
    action()
