from JumpScale import j

descr = """
Scheduler that runs on master to check for orphan disks on specific volumedriver nodes

Generates warning if orphan disks exist on the specified volumes
"""

organization = 'cloudscalers'
category = "monitor.healthcheck"
author = "deboeckj@codescalers.com"
version = "1.0"

enable = True
async = True
period = 3600 # 1 hrs
roles = ['master',]
queue = 'process'


def action():
    acl = j.clients.agentcontroller.get()
    ccl = j.clients.osis.getNamespace('cloudbroker')

    results = []
    for location in ccl.location.search({})[1:]:
        job = acl.executeJumpscript('cloudscalers', 'disk_orphan', role='storagedriver', gid=location['gid'])
        if job['state'] == 'OK':
            results.extend(job['result'])

    if not results:
        results.append({'state': 'OK', 'category': 'Orphanage', 'message': 'No orphan disks found.'})
    return results

if __name__ == '__main__':
    j.core.osis.client = j.clients.osis.getByInstance('main')
    print action()
