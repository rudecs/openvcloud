
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'Name Servers', 'VLan ID', 'CloudSpace ID', 'Stack ID', 'Subnet', 'NetMask', 'Description']

    def makeNS(row, field):
        return str(', '.join(row[field])) or ' '

    def makeID(row, field):
        return '[%s|CBGrid/network?id=%s]' % (row[field], row[field]) if row[field] else ' '

    def makeVLAN(row, field):
        return '[%s|CBGrid/vlan?id=%s]' % (row[field], row[field]) if row[field] else ' '

    def makeCS(row, field):
        return '[%s|CBGrid/cloudspace?id=%s]' % (row[field], row[field]) if row[field] else ' '

    def makeStack(row, field):
        link = ('[%s|CBGrid/stack?id=%s]' % (row[field], row[field]))
        return link or ' '

    fieldids = ['id', 'name', 'nameservers', 'vlanId', 'cloudspaceId', 'stackId', 'subnet', 'netmask', 'descr']
    fieldvalues = [makeID, 'name', makeNS, makeVLAN, makeCS, makeStack, 'subnet', 'netmask', 'descr']
    tableid = modifier.addTableForModel('cloudbroker', 'network', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
