
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    nativequery = None
    cloudspaceid = args.getTag('space')
    if cloudspaceid:
        cloudspaceid = int(cloudspaceid)
        args.tags.tags.pop('space')
        cbclient = j.core.osis.getClientForNamespace('cloudbroker')

        if not cbclient.cloudspace.exists(cloudspaceid):
            page.addMessage('could not find cloudspace with id "%s"' % cloudspaceid)
            params.result = page
            return params

        stackids = cbclient.cloudspace.get(cloudspaceid).resourceProviderStacks
        stacks = cbclient.stack.simpleSearch({}, nativequery={'query': {'bool': {'must': [{'terms': {'id': set(stackids)}}]}}})
        nodenames = [str(stack['referenceId']) for stack in stacks]

        nativequery = {'query': {'bool': {'must': [{'terms': {'name': nodenames}}]}}}

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        filters[tag] = val

    fieldnames = ['ID', 'Name', 'IP Addresses']

    def makeIPs(row, field):
        return str(', '.join(row[field]))

    fieldids = ['id', 'name', 'ipaddr']
    fieldvalues = ['[%(id)s|/Grid/node?id=%(id)s]', 'name', makeIPs]
    tableid = modifier.addTableForModel('system', 'node', fieldids, fieldnames, fieldvalues, filters, nativequery=nativequery)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
