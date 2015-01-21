
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    cloudspaceid = args.getTag('space')
    if cloudspaceid:
        cloudspaceid = int(cloudspaceid)
        args.tags.tags.pop('space')
        cbclient = j.core.osis.getClientForNamespace('cloudbroker')

        if not cbclient.cloudspace.exists(cloudspaceid):
            page.addMessage('could not find cloudspace with id "%s"' % cloudspaceid)
            params.result = page
            return params

        stackids = list(set(cbclient.cloudspace.get(cloudspaceid).resourceProviderStacks))
        stacks = cbclient.stack.search({'id': {'$in': stackids}})[1:]
        nodeids = [ int(stack['referenceId']) for stack in stacks]
        filters['id'] = nodeids

    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'IP Addresses']

    def makeIPs(row, field):
        return str(', '.join(row[field]))

    fieldids = ['id', 'name', 'ipaddr']
    fieldvalues = ['[%(id)s|/Grid/node?id=%(id)s&gid=%(gid)s]', 'name', makeIPs]
    tableid = modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
