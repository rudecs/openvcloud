import json
import sys
from JumpScale import j
def do(username):
    data = {}
    import JumpScale.grid
    scl = j.core.osis.getClientForNamespace('system')
    ccl = j.core.osis.getClientForNamespace('cloudbroker')
    bcl = j.core.osis.getClientForNamespace('billing')
    lcl = j.core.osis.getClientForNamespace('libcloud')
    lclvrt = j.core.osis.getClientForNamespace('libvirt')
    vcl = j.core.osis.getClientForNamespace('vfw')
    grid = scl.grid.get(j.application.whoAmI.gid)
    locationname = grid.name
    user = scl.user.simpleSearch({'id': username})
    if not user:
        print "Could not find user"
        sys.exit(0)

    data['user'] = scl.user.get(user[0]['guid']).dump()
    data['group'] = scl.group.get(user[0]['guid']).dump()
    accounts = ccl.account.simpleSearch({'name': username})
    if not accounts:
        print 'Could not find account'
        sys.exit(0)
    accountId = accounts[0]['id']
    data['account'] = ccl.account.get(accountId).dump()
    data['sizes'] = ccl.size.simpleSearch({})
    data['images'] = ccl.image.simpleSearch({})
    data['stacks'] = ccl.stack.simpleSearch({})
    data['transactions'] = ccl.credittransaction.simpleSearch({'accountId': accountId})
    for transaction in data['transactions']:
        if transaction['reference']:
            bill = bcl.billingstatement.get(transaction['reference'])
            if bill:
                transaction['bill'] = bill.dump()
    cloudspaces = list()
    data['cloudspaces'] = cloudspaces
    for cloudspace in ccl.cloudspace.simpleSearch({'accountId': accountId}):
        if cloudspace['status'] != 'DESTROYED' and cloudspace['location'] == locationname:
            cloudspaces.append(cloudspace)
    vmachines = list()
    disks = list()
    data['vmachines'] = vmachines
    data['disks'] = disks
    vfws = list()
    data['vfws'] = vfws
    for cloudspace in data['cloudspaces']:
        for vmachine in ccl.vmachine.simpleSearch({'cloudspaceId': cloudspace['id']}):
            if vmachine['status'] != 'DESTROYED':
                vmachine['xml'] = lcl.libvirtdomain.get('domain_%(referenceId)s' % vmachine)
                vmachine['node'] = lclvrt.node.get(vmachine['referenceId']).dump()
                vmachines.append(vmachine)
                for disk in vmachine['disks']:
                    disks.append(ccl.disk.get(disk).dump())
        for vfw in vcl.virtualfirewall.simpleSearch({'domain': str(cloudspace['id'])}):
            node = scl.node.get("%(gid)s_%(nid)s" % vfw)
            vfw['nodename'] = node.name
            vfws.append(vfw)

    with open('%s.json' % username, 'w') as fd:
        json.dump(data, fd)
    #print data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username')
    opts = parser.parse_args()
    do(opts.username)
