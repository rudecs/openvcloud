from JumpScale import j

descr = """
Checks on volumedriver node for orphan disks

Generates warning if orphan disks exist on the specified volumes
"""

organization = 'cloudscalers'
category = "monitor"
author = "deboeckj@codescalers.com"
version = "1.0"

enable = True
async = True
roles = ['cpunode',]
queue = 'process'

def action():
    import os
    from CloudscalerLibcloud import openvstorage
    cbcl = j.clients.osis.getNamespace('cloudbroker', j.core.osis.client)
    vcl = j.clients.osis.getNamespace('vfw', j.core.osis.client)
    disks = cbcl.disk.search({'$fields': ['status', 'referenceId']}, size=0)[1:]
    diskmap = {openvstorage.getPath(disk['referenceId']): disk['status'] for disk in disks}
    networks = vcl.virtualfirewall.search({'$fields': ['id'], '$query': {'gid': j.application.whoAmI.gid}}, size=0)[1:]
    activenetworks = [network['id'] for network in networks]
    results = []

    vmstor = '/mnt/vmstor'
    def process(_, folder, files):
        if 'templates' in files:
            files.remove('templates')
        if 'archive' in files:
            files.remove('archive')
        for file_ in files:
            if file_.startswith('ovs-healthcheck-test'):
                continue
            fullpath = os.path.join(folder, file_)
            if file_.endswith('.raw'):
                if 'routeros' in file_:
                    networkid = int(os.path.basename(folder), 16)
                    if networkid not in activenetworks:
                        results.append({'state': 'WARNING', 'category': 'Orphanage', 'message': 'Found orphan disk %s' % fullpath, 'uid': 'Found orphan disk %s' % fullpath})
                elif file_.startswith('cloud-init') and len(files) == 1:
                    results.append({'state': 'WARNING', 'category': 'Orphanage', 'message': 'Found orphan cloud-init %s' % fullpath, 'uid': 'Found orphan cloud-init %s' % fullpath})
                else:
                    diskstatus = diskmap.get(fullpath, 'DESTROYED')
                    if diskstatus == 'DESTROYED':
                        results.append({'state': 'WARNING', 'category': 'Orphanage', 'message': 'Found orphan disk %s' % fullpath, 'uid': 'Found orphan disk %s' % fullpath})
        if not files:
            results.append({'state': 'WARNING', 'category': 'Orphanage', 'message': 'Found empty folder %s' % folder, 'uid': 'Found empty folder %s' % folder})


    os.path.walk(vmstor, process, None)

    return results

if __name__ == '__main__':
    j.core.osis.client = j.clients.osis.getByInstance('main')
    print action()
