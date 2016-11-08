
def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    ccl = j.clients.osis.getNamespace('cloudbroker')

    stackid = args.getTag('stackid')
    filters = dict()
    if stackid:
        stackid = int(stackid)
        stack = ccl.stack.get(stackid)
        images = ccl.image.search({'id': {'$in': stack.images}})[1:]
        imageids = [image['referenceId'] for image in images]
        filters['id'] = {'$in': imageids}

    locations = ccl.location.search({'$query': {}, '$fields': ['gid', 'name']})[1:]
    locationmap = {loc['gid']: loc['name'] for loc in locations}

    def getLocation(field, row):
        gid = field[row]
        if not gid:
            return ''
        name = locationmap[gid]
        return "[{name} ({gid})|/cbgrid/grid?gid={gid}]".format(gid=gid, name=name)

    fields = [
        {'name': 'Location',
         'id': 'gid',
         'value': getLocation
         },
        {'name': 'Name',
         'id': 'name',
         'value': "<a href='/cbgrid/image?id=%(id)s'>%(name)s</a>"
         },
        {'name': 'Type',
         'id': 'type',
         'value': 'type'
         },
        {'name': 'Size',
         'id': 'size',
         'type': 'int',
         'value': '%(size)s GiB'
         },
    ]
    tableid = modifier.addTableFromModel('libvirt', 'image', fields, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
