import json
import sys
import os
from JumpScale import j

def load(path, credit):
    def loadfile(path):
        with open(path) as fd:
            data = json.load(fd)
        username, _ = os.path.splitext(j.system.fs.getBaseName(path))
        do(username, data, credit)

    if j.system.fs.isFile(path):
        loadfile(path)
    elif j.system.fs.isDir(path):
        for filepath in j.system.fs.listFilesInDir(path, filter='*.json'):
            loadfile(filepath)


def do(username, data, credit):
    import JumpScale.grid
    scl = j.clients.osis.getNamespace('system')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    vcl = j.clients.osis.getNamespace('vfw')
    lcl = j.clients.osis.getNamespace('libcloud')
    lclvrt = j.clients.osis.getNamespace('libvirt')
    locations = { location['locationCode']: location['gid'] for location in ccl.location.search({})[1:] }
    locationmap = {301: 'lenoir2.vscalers.com', 400: 'york1.vscalers.com'}
    disksbyid = { disk['id']: disk for disk in data['disks'] }


    groups = scl.group.simpleSearch({'id': username})
    if not groups:
        scl.group.set(data['group'])

    user = scl.group.simpleSearch({'id': username})[0]

    user = scl.user.get(user['guid'])
    for prop in ('domain', 'description', 'roles', 'passwd', 'emails', 'authkey', 'lastcheck'):
        if not getattr(user, prop):
            setattr(user, prop, data['user'][prop])
    scl.user.set(user)


    accounts = ccl.account.simpleSearch({'name': username})
    if not accounts:
        data['account'].pop('id', None)
        accountId, _, _ = ccl.account.set(data['account'])
    else:
        accountId = accounts[0]['id']
    print 'AccountId %s for user %s' % (accountId, username)

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

    def getStacksWithImage(imageId):
        stacks = list()
        for stack in data['stacks']:
            if imageId in stack.get('images', list()):
                stacks.append(stack['id'])
        return stacks

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
                images = ccl.image.search({'name': image['name']})[1:]
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

    for accountimage in data['accountimages']:
        accountimage['accountId'] = accountId
        gid = accountimage.pop('gid')
        oldid = accountimage.pop('id', None)
        accountimage.pop('guid', None)
        reference = accountimage.pop('reference', None)
        accountimage['type'] = 'Custom Templates'
        reference['type'] = 'Custom Templates'
        lclvrt.image.set(reference)
        newimageid, _, _ = ccl.image.set(accountimage)
        for oldstackid in getStacksWithImage(oldid):
            stackId = getNewStackId(gid, oldstackid)
            stack = ccl.stack.get(stackId)
            if newimageid not in stack.images:
                stack.images.append(newimageid)
                ccl.stack.set(stack)
            provid = '%s_%s' % (stack.gid, stack.referenceId)
            provider = lclvrt.resourceprovider.get(provid)
            if reference['guid'] not in provider.images:
                provider.images.append(reference['guid'])
                lclvrt.resourceprovider.set(provider)


    cloudspacemapping = dict()
    for cloudspace in data['cloudspaces']:
        oldspaceid = cloudspace.pop('id', None)
        cloudspace['accountId'] = accountId
        cloudspace['gid'] = locations[cloudspace['location']]
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
    parser.add_argument('-p', '--path', help="File path or folderpath")
    parser.add_argument('-c', '--credit', action='store_true', default=False)
    opts = parser.parse_args()
    load(opts.path, opts.credit)

