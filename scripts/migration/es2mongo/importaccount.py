import json
import sys
from JumpScale import j
def do(username, credit):
    with open('%s.json' % username) as fd:
        data = json.load(fd)
    import JumpScale.grid
    scl = j.core.osis.getClientForNamespace('system')
    ccl = j.core.osis.getClientForNamespace('cloudbroker')
    bcl = j.core.osis.getClientForNamespace('billing')
    vcl = j.core.osis.getClientForNamespace('vfw')
    lcl = j.core.osis.getClientForNamespace('libcloud')
    lclvrt = j.core.osis.getClientForNamespace('libvirt')
    locations = { location['locationCode']: location['gid'] for location in ccl.location.search({})[1:] }
    locationmap = {301: 'lenoir2.vscalers.com', 400: 'york1.vscalers.com'}
    disksbyid = { disk['id']: disk for disk in data['disks'] }


    groups = scl.group.simpleSearch({'id': username})
    if not groups:
        scl.group.set(data['group'])

    user = scl.user.simpleSearch({'id': username})
    if not user:
        scl.user.set(data['user'])

    accounts = ccl.account.simpleSearch({'name': username})
    if not accounts:
        data['account'].pop('id', None)
        accountId, _, _ = ccl.account.set(data['account'])
    else:
        accountId = accounts[0]['id']
    print 'AccountId %s for user %s' % (accountId, username)

    if credit:
        for transaction in data['transactions']:
            bill = transaction.pop('bill', None)
            billId = None
            if bill:
                bill.pop('guid', None)
                bill.pop('id', None)
                bill['accountId'] = accountId
                billId, _,_ = bcl.billingstatement.set(bill)
            transaction.pop('id', None)
            transaction.pop('guid', None)
            transaction['accountId'] = accountId
            transaction['reference'] = billId
            ccl.credittransaction.set(transaction)
        print 'Done'
        sys.exit(0)

    def getNewStackId(gid, stackId):
        for stack in data['stacks']:
            if stack['id'] == stackId:
                stackname = stack['referenceId']
                stacks = ccl.stack.search({'name': stackname, 'gid': gid})[1:]
                if not stacks:
                    stackname = "%s.%s" % (stackname, locationmap[gid])
                    stacks = ccl.stack.search({'name': stackname, 'gid': gid})[1:]
                    if not stacks:
                        print "Could not find stack for gid: %s with name:%s" % (gid, stackname)
                        return 0
                return stacks[0]['id']

    def getNewSize(sizeId):
        for size in data['sizes']:
            if size['id'] == sizeId:
                sizes = ccl.size.search({'vcpus': size['vcpus'], 'memory': size['memory']})[1:]
                if not sizes:
                    print "Could not find size with id:%" % sizeId
                    return 0
                return sizes[0]['id']

    def getNewImage(imageId):
        for image in data['images']:
            if image['id'] == imageId:
                images = ccl.image.search({'name': image['name'], 'size': image['size']})[1:]
                if not images:
                    print "Could not find image %s" % image
                    return 0
                return images[0]['id']

    def getNid(gid, name):
        nodes = scl.node.search({'gid': gid, 'name': name})[1:]
        if not nodes:
            name = "%s.%s" % (name, locationmap[gid])
            nodes = scl.node.search({'gid': gid, 'name': name})[1:]
            if not nodes:
                print "Could not find node on gid: %s with name: %s" % (gid, name)
                return 0
        return nodes[0]['id']

    cloudspacemapping = dict()
    for cloudspace in data['cloudspaces']:
        oldspaceid = cloudspace.pop('id', None)
        cloudspacemapping = dict()
        cloudspace['gid'] = locations[cloudspace['location']]
        cloudspace['accountId'] = accountId
        cloudspaceId, _, _ = ccl.cloudspace.set(cloudspace)
        cloudspacemapping[oldspaceid] = cloudspaceId
        for vm in data['vmachines']:
            if vm['cloudspaceId'] == oldspaceid:
                vm['cloudspaceId'] = cloudspaceId
                vm['sizeId'] = getNewSize(vm['sizeId'])
                vm['imageId'] = getNewImage(vm['imageId'])
                vm['stackId'] = getNewStackId(cloudspace['gid'], vm['stackId'])
                diskids = vm['disks']
                newdiskids = list()
                vm['disks'] = newdiskids
                for diskid in diskids:
                    disk = disksbyid[diskid]
                    disk.pop('id', None)
                    newdisksid, _, _ = ccl.disk.set(disk)
                    newdiskids.append(newdisksid)
                xml = vm.pop('xml', None)
                if xml:
                    lcl.libvirtdomain.set(xml, 'domain_%(referenceId)s' % vm)
                node = vm.pop('node', None)
                if node:
                    lclvrt.node.set(node)
                ccl.vmachine.set(vm)

    for vfw in data['vfws']:
        nodename = vfw.pop('nodename')
        nid = getNid(vfw['gid'], nodename)
        vfw['nid'] = nid
        vfw['password'] = 'Dct007'
        vfw['domain'] = str(cloudspacemapping[int(vfw['domain'])])
        vcl.virtualfirewall.set(vfw)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username')
    parser.add_argument('-c', '--credit', action='store_true', default=False)
    opts = parser.parse_args()
    do(opts.username, opts.credit)
