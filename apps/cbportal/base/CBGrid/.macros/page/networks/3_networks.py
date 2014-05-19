
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'Name Servers', 'VLan ID', 'CloudSpace ID', 'Stack ID', 'Subnet', 'NetMask', 'Description']

    def makeNS(row, field):
        return str(', '.join(row[field]))

    fieldids = ['id', 'name', 'nameservers', 'vlanId', 'cloudspaceId', 'stackId', 'subnet', 'netmask', 'descr']
    fieldvalues = ['[%(id)s|/CBGrid/network?id=%(id)s]', 'name', makeNS, 
                   '[%(vlanId)s|/CBGrid/vlan?id=%(vlanId)s]', 
                   '[%(cloudspaceId)s|/CBGrid/cloudspace?id=%(cloudspaceId)s]',
                   '[%(stackId)s|/CBGrid/stack?id=%(stackId)s]', 
                   'subnet', 'netmask', 'descr']
    tableid = modifier.addTableForModel('cloudbroker', 'network', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
