
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'Account ID', 'Network ID', 'Resource Provider Stacks', 'Status', 'Access Control List', 'Description', 'Public IP Address', 'Resource Limits']

    def makeACL(row, field):
        return str('<br>'.join(['%s:%s' % (acl['userGroupId'], acl['right']) for acl in row[field]]))

    def makeRL(row, field):
        resourceLimits = list()
        for k, v in row[field].iteritems():
            resourceLimits.append('%s: %s'% (k, str(v)))
        return str('<br>'.join(resourceLimits))

    def makeID(row, field):
        return '[%s|CBGrid/cloudspace?id=%s]' % (row[field], row[field])

    def makeNW(row, field):
        return '[%s|CBGrid/network?id=%s]' % (row[field], row[field])

    def makeACC(row, field):
        return '[%s|CBGrid/account?id=%s]' % (row[field], row[field])

    def makeRPS(row, field):
        links = [' ']
        for rps in row[field]:
            links.append('[%s|CBGrid/stack?id=%s]' % (rps, rps))
        return ', '.join(links)

    fieldids = ['id', 'name', 'accountId', 'networkId', 'resourceProviderStacks', 'status', 'acl', 'descr', 'publicipaddress', 'resourceLimits']
    fieldvalues = [makeID, 'name', makeACC, makeNW, makeRPS, 'status', makeACL, 'descr', 'publicipaddress', makeRL]
    tableid = modifier.addTableForModel('cloudbroker', 'cloudspace', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
