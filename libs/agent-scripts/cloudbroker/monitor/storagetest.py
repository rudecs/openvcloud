from JumpScale import j
descr = """
check status of alertservice
"""

organization = 'cloudscalers'
name = 'storagestest'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['cpunode']
period = 60 * 30 # 30min
enable = True
async = False
log = True

def action():
    import time
    import re
    import netaddr
    ACCOUNTNAME = 'test_storage'
    pcl = j.clients.portal.getByInstance('main')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    accounts = ccl.account.search({'name': ACCOUNTNAME})[1:]
    loc = ccl.location.search({})[1]['locationCode']
    if not accounts:
        print 'Creating Account'
        accountId = pcl.actors.cloudbroker.account.create(ACCOUNTNAME, 'admin', None, loc)
    else:
        print 'Found Account'
        accountId = accounts[0]['id']
    cloudspace = ccl.cloudspace.search({'accountId': accountId})[1:][0]
    if cloudspace['status'] == 'VIRTUAL':
        print 'Deploying CloudSpace'
        pcl.actors.cloudbroker.cloudspace.deployVFW(cloudspace['id'])

    imageId = ccl.image.search({'name': 'Ubuntu 14.04 x64'})[1]['id']
    size = ccl.size.search({'memory': 512})[1]
    sizeId = size['id']
    diskSize = min(size['disks'])
    timestamp = time.ctime()

    stack = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1]
    name = '%s on %s' % (timestamp, stack['name'])
    print 'Deploying VM'
    vmachineId = pcl.actors.cloudbroker.machine.createOnStack(cloudspaceId=cloudspace['id'], name=name,
                                                 imageId=imageId, sizeId=sizeId,
                                                 disksize=diskSize, stackid=stack['id'])
    now = time.time()
    ip = 'Undefined'
    while now + 60 > time.time() and ip == 'Undefined':
        print 'Waiting for IP'
        time.sleep(5)
        vmachine = pcl.actors.cloudapi.machines.get(vmachineId)
        ip = vmachine['interfaces'][0]['ipAddress']

    publicports = [1999]
    for forward in pcl.actors.cloudapi.portforwarding.list(cloudspace['id']):
        publicports.append(int(forward['publicPort']))
    publicport = max(publicports) + 1

    pcl.actors.cloudapi.portforwarding.create(cloudspace['id'], cloudspace['publicipaddress'], publicport, vmachineId, 22, 'tcp')
    publicip = str(netaddr.IPNetwork(cloudspace['publicipaddress']).ip)
    account = vmachine['accounts'][0]
    connection = j.remote.cuisine.connect(publicip, publicport, account['password'], account['login'])
    connection.user(account['login'])
    output = connection.run("dd if=/dev/zero of=500mb.dd bs=4k count=128k")
    try:
        print 'Perfoming internet test'
        connection.run('ping -c 1 8.8.8.8')
    except:
        msg = "Could not connect to internet from vm on nodes %s" % stack['name']
        print msg
        eco = j.errorconditionhandler.getErrorConditionObject(msg=msg, category='monitoring', level=1, type='OPERATIONS')
        eco.process()

    match = re.search('^\d+.*copied,.*?, (?P<speed>.*?)B/s$', output, re.MULTILINE).group('speed').split()
    speed = j.tools.units.bytes.toSize(float(match[0]), match[1], 'M')
    msg = 'Measured write speed on disk was %sMB/s on Node %s' % (speed, stack['name'])
    status = 'OK'
    print msg
    if speed < 50:
        status = 'WARNING'
        eco = j.errorconditionhandler.getErrorConditionObject(msg=msg, category='monitoring', level=1, type='OPERATIONS')
        eco.process()
    pcl.actors.cloudapi.machines.delete(vmachineId)
    return [{'message': msg, 'category': 'Storage Test', 'state': status}]

if __name__ == '__main__':
    print action()
