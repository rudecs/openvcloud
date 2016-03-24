from JumpScale import j
descr = """
check status of alertservice
"""

organization = 'cloudscalers'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['cpunode']
period = 60 * 30 # 30min
timeout = 60 * 5
enable = True
async = True
queue = 'io'
log = True

def action():
    import time
    import re
    import netaddr
    category = 'Deployment Test'
    ACCOUNTNAME = 'test_storage'
    pcl = j.clients.portal.getByInstance('main')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    accounts = ccl.account.search({'name': ACCOUNTNAME, 'status': 'CONFIRMED'})[1:]
    loc = ccl.location.search({})[1]['locationCode']
    images = ccl.image.search({'name': 'Ubuntu 14.04 x64'})[1:]
    if not images:
        return [{'message': "Image not available (yet)", 'category': category, 'state': "SKIPPED"}]
    imageId = images[0]['id']

    if not accounts:
        j.console.echo('Creating Account', log=True)
        accountId = pcl.actors.cloudbroker.account.create(ACCOUNTNAME, 'admin', None, loc)
    else:
        j.console.echo('Found Account', log=True)
        accountId = accounts[0]['id']
    cloudspaces = ccl.cloudspace.search({'accountId': accountId,
                                        'status': {'$in': ['VIRTUAL', 'DEPLOYED']}
                                       })[1:]
    if not cloudspaces:
        msg = "No cloudspace available for account %s, disabling test" % ACCOUNTNAME
        return [{'message': msg, 'category': category, 'state': 'OK'}]
    else:
        cloudspace = cloudspaces[0]

    if cloudspace['status'] == 'VIRTUAL':
        j.console.echo('Deploying CloudSpace', log=True)
        pcl.actors.cloudbroker.cloudspace.deployVFW(cloudspace['id'])
        cloudspace = ccl.cloudspace.get(cloudspace['id']).dump()

    size = ccl.size.search({'memory': 512})[1]
    sizeId = size['id']
    diskSize = min(size['disks'])
    timestamp = time.ctime()

    stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
    if stack['status'] != 'ENABLED':
        return [{'message': 'Disabling test stack is not enabled', 'category': category, 'state': 'OK'}]

    name = '%s on %s' % (timestamp, stack['name'])
    j.console.echo('Deleting vms older then 24h', log=True)
    vms = ccl.vmachine.search({'stackId': stack['id'],
                               'cloudspaceId': cloudspace['id'],
                               'status': {'$nin': ['ERROR', 'DESTROYED']}
                               })[1:]
    for vm in vms:
        try:
            if time.time() - vm['creationTime'] > 3600 * 24:
                j.console.echo('Deleting %s' % vm['name'], log=True)
                pcl.actors.cloudapi.machines.delete(vm['id'])
        except Exception, e:
            j.console.echo('Failed to delete vm %s' % e, log=True)
    vms = ccl.vmachine.search({'stackId': stack['id'], 'cloudspaceId': cloudspace['id'], 'status': 'RUNNING'})[1:]
    if vms:
        vmachineId = vms[0]['id']
        vmachine = pcl.actors.cloudapi.machines.get(vmachineId)
        j.console.echo('Found VM %s' % vmachine['name'], log=True)
    else:
        j.console.echo('Deploying VM', log=True)
        vmachineId = pcl.actors.cloudbroker.machine.createOnStack(cloudspaceId=cloudspace['id'], name=name,
                                                 imageId=imageId, sizeId=sizeId,
                                                 disksize=diskSize, stackid=stack['id'])
        vmachine = pcl.actors.cloudapi.machines.get(vmachineId)
    now = time.time()
    status = 'OK'
    try:
        ip = vmachine['interfaces'][0]['ipAddress']
        while now + 60 > time.time() and ip == 'Undefined':
            j.console.echo('Waiting for IP', log=True)
            time.sleep(5)
            vmachine = pcl.actors.cloudapi.machines.get(vmachineId)
            ip = vmachine['interfaces'][0]['ipAddress']

        j.console.echo('Got IP %s' % ip, log=True)
        publicports = []
        publicport = 0
        for forward in pcl.actors.cloudapi.portforwarding.list(cloudspace['id']):
            if forward['localIp'] == ip and forward['localPort'] == '22':
                publicport = forward['publicPort']
                break
            publicports.append(int(forward['publicPort']))
        if publicport == 0:
            publicport = 2000 + j.application.whoAmI.nid * 100
            while publicport in publicports:
                publicport += 1
            j.console.echo('Creating portforward', log=True)
            pcl.actors.cloudapi.portforwarding.create(cloudspace['id'], cloudspace['publicipaddress'], publicport, vmachineId, 22, 'tcp')

        publicip = str(netaddr.IPNetwork(cloudspace['publicipaddress']).ip)
        account = vmachine['accounts'][0]
        j.console.echo('Waiting for public connection', log=True)
        if not j.system.net.waitConnectionTest(publicip, publicport, 60):
            j.console.echo('Failed to get public connection %s:%s' % (publicip, publicport), log=True)
            status = 'ERROR'
            msg = 'Could not connect to VM over public interface'
        else:
            def runtests():
                status = 'OK'
                j.console.echo('Connecting over ssh', log=True)
                connection = j.remote.cuisine.connect(publicip, publicport, account['password'], account['login'])
                connection.user(account['login'])
                connection.fabric.api.env['abort_on_prompts'] = True
                connection.fabric.api.env['abort_exception'] = RuntimeError

                j.console.echo('Running dd', log=True)
                try:
                    output = connection.run("rm -f 500mb.dd; dd if=/dev/zero of=500mb.dd bs=4k count=128k")
                except Exception, e:
                    status = "ERROR"
                    msg = "Failed to run dd command. Login error? %s" % e
                    return status, msg

                try:
                    j.console.echo('Perfoming internet test', log=True)
                    connection.run('ping -c 1 8.8.8.8')
                except:
                    msg = "Could not connect to internet from vm on node %s" % stack['name']
                    j.console.echo(msg, log=True)
                    status = 'ERROR'
                    return status, msg

                match = re.search('^\d+.*copied,.*?, (?P<speed>.*?)B/s$', output, re.MULTILINE).group('speed').split()
                speed = j.tools.units.bytes.toSize(float(match[0]), match[1], 'M')
                msg = 'Measured write speed on disk was %sMB/s on Node %s' % (speed, stack['name'])
                j.console.echo(msg, log=True)
                if speed < 50:
                    status = 'WARNING'
                return status, msg

            status, msg = runtests()
        if status != 'OK':
            eco = j.errorconditionhandler.getErrorConditionObject(msg=msg, category='monitoring', level=1, type='OPERATIONS')
            eco.process()
    except:
        j.console.echo('Deleting test vm', log=True)
        pcl.actors.cloudapi.machines.delete(vmachineId)
        j.console.echo('Finished deleting test vm', log=True)
        raise
    return [{'message': msg, 'category': 'Storage Test', 'state': status}]

if __name__ == '__main__':
    print action()
