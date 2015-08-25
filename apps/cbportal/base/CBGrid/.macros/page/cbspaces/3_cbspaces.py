import ujson as json

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    accountId = args.getTag('accountId')
    if accountId:
        filters['accountId'] = int(accountId)

    fieldnames = ['ID', 'Name', 'User Name', 'Network ID', 'Stacks IDs', 'Location', 'Status', 'Public IP Address']

    def _formatData():
        res = list()
        cl = j.clients.osis.getNamespace('cloudbroker')
        for cs in cl.cloudspace.list():
            cloudspace = cl.cloudspace.get(cs)
            accountId = cloudspace.accountId
            user  = cl.account.get(accountId)
            id = '<a href="/CBGrid/cloudspace?id=%s">%s</a>' % (cloudspace.id, cloudspace.id)
            username = '<a href="/CBGrid/account?id=%s">%s</a>' % (accountId, user.name)
            networkId = ''
            rps = ''
            if cloudspace.networkId:
                networkId = '<a href="/CBGrid/network?id=%s&gid=%s">%s</a>' % (cloudspace.networkId, cloudspace.gid, cloudspace.networkId)
            if cloudspace.resourceProviderStacks:
                rps = ','.join(['<a href="/CBGrid/stack?id=%s">%s</a>' % (sid, sid) for sid in cloudspace.resourceProviderStacks])
            res.append([id, cloudspace.name, username,  networkId, rps, cloudspace.location, cloudspace.status, cloudspace.publicipaddress or ''])
        return json.dumps(res)
    
    fieldvalues = _formatData()
    tableid = modifier.addTableFromData(fieldvalues, fieldnames)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
