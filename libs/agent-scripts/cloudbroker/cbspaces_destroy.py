import time
from JumpScale import j


descr = """
Permanently removes cloudspaces with status deleted if the configured period for this grid has passed since deletion. (Empties the trash can)
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
period = "0 * * * *"
timeout = 900

def action():
    from CloudscalerLibcloud.utils.gridconfig import GridConfig
    ccl = j.clients.osis.getNamespace('cloudbroker')
    current_time = time.time()
    cloudspaces = ccl.cloudspace.search({'status': 'DELETED'}, size=0)[1:]
    scl = j.clients.osis.getNamespace('system')
    pcl = j.clients.portal.getByInstance('main')
    for cloudspace in cloudspaces:
        deletion_time = cloudspace['deletionTime']
        grid_id = cloudspace['gid']
        grid = scl.grid.get(grid_id)
        grid_config = GridConfig(grid)
        retention_period = grid_config.get('delete_retention_period')
        if current_time >= (deletion_time + retention_period):
            pcl.actors.cloudbroker.cloudspace.destroy(cloudspaceId=cloudspace['id'], permanently=True, reason='Cleanup job')



if __name__ == '__main__':
    action()
