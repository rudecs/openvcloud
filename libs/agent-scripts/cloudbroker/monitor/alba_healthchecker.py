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
    from ovs.dal.lists.albanodelist import AlbaNodeList
    result = list()

    nodeip = j.system.net.getIpAddress('backplane1')[0][0]
    node = AlbaNodeList.get_albanode_by_ip(nodeip)
    if node:
        for disk in node.all_disks:
            r = {}
            state = 'OK' if disk['state']['state'] == 'ok' else 'ERROR'
            r['category'] = 'ALBA healthcheck'
            r['state'] = state
            r['message'] = "DISK %(name)s" % disk
            result.append(r)
            if state != 'OK':
                r['message'] += ' Error: %s' % disk['state'].get('detail', 'UNKNOWN')
                eco = j.errorconditionhandler.getErrorConditionObject(msg=r['message'], category='monitoring', level=1, type='OPERATIONS')
                eco.process()
    if not result:
        result.append({'category': 'ALBA healthcheck', 'state': 'OK', 'message': 'Not an active alba node'})

    return result

if __name__ == '__main__':
    print action()