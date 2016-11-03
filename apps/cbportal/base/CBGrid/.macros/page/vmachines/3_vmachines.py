
def main(j, args, params, tags, tasklet):
    import cgi
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    stackid = args.getTag("stackid")
    cloudspaceId = args.getTag("cloudspaceid")
    imageid = args.getTag('imageid')
    gid = args.getTag('gid')
    filters = dict()
    ccl = j.clients.osis.getNamespace('cloudbroker')

    if stackid:
        stackid = int(stackid)
        filters['stackId'] = stackid
    if cloudspaceId:
        filters['cloudspaceId'] = int(cloudspaceId)
    if imageid:
        imageid = str(imageid)
        images = ccl.image.search({'referenceId': imageid})[1:]
        if images:
            filters['imageId'] = images[0]['id']
        else:
            filters['imageId'] = imageid

    if gid:
        gid = int(gid)
        stacks = ccl.stack.simpleSearch({'gid': gid})
        stacksids = [stack['id'] for stack in stacks]
        filters['stackId'] = {'$in':stacksids}

    fieldnames = ['Name', 'Host Name', 'Status', 'Created at', 'Updated at', 'Cloud Space ID', 'Stack ID']

    def stackLinkify(row, field):
        return '[%s|stack?id=%s]' % (row[field], row[field])

    def nameLinkify(row, field):
        val = row[field]
        if not isinstance(row[field], int):
            val  = cgi.escape(row[field])
        return '[%s|Virtual Machine?id=%s]' % (val, row['id'])

    def spaceLinkify(row, field):
        return '[%s|cloud space?id=%s]' % (row[field], row[field])

    fields = [
        {
            'name': 'name',
            'value': nameLinkify,
            'id': 'id'
        }, {
            'name': 'hostName',
            'value': 'name',
            'id': 'hostName'
        }, {
            'name': 'status',
            'value': 'status',
            'id': 'status'
        }, {
            'name': 'cloudspaceId',
            'value': spaceLinkify,
            'id': 'cloudspaceId'
        }, {
            'name': 'stackId',
            'value': stackLinkify,
            'id': 'stackId'
        }, {
            'name': 'creationTime',
            'value': modifier.makeTime,
            'id': 'creationTime',
            'type': 'date'
        }, {
            'name': 'updateTime',
            'value': modifier.makeTime,
            'id': 'updateTime',
            'type': 'date'
        }
    ]

    tableid = modifier.addTableFromModel('cloudbroker', 'vmachine', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
