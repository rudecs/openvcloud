from JumpScale import j

organization = "openvstorage"
descr = 'Perform Disk checks on ALBA'
author = "hamdy.farag@codescalers.com"
order = 1
enable = True
async = True
log = True
queue = 'io'
period = 30 * 60
roles = ['storagenode']
category = "monitor.healthcheck"

def action():
    import sys
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.albabackendlist import AlbaBackendList
    result = list()

    for backend in AlbaBackendList.get_albabackends():
        for disk in backend.all_disks:
            for ip in disk['ips']:
                if j.system.net.isIpLocal(ip):
                    break
            else:
                continue
            r = {}
            state = 'OK' if disk['state']['state'] == 'ok' else 'ERROR'
            r['category'] = 'ALBA healthcheck'
            r['state'] = state
            r['message'] = "Backend '%s'  DISK %s" % (backend.name, disk['name'])
            result.append(r)
            if state != 'OK':
                r['message'] += ' Error: %s' % disk['state'].get('detail', 'UNKNOWN')
                eco = j.errorconditionhandler.getErrorConditionObject(msg=r['message'], category='monitoring', level=1, type='OPERATIONS')
                eco.process()
    return result

if __name__ == '__main__':
    print action()