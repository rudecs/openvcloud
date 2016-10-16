

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()
    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fieldnames = ['GID', 'Name', 'Location Code']

    fieldids = ['gid', 'name', 'flag', 'locationCode']
    fieldvalues = ['[%(gid)s|/CBGrid/grid?gid=%(gid)s]', 'name', 'locationCode']
    tableid = modifier.addTableForModel('cloudbroker', 'location', fieldids, fieldnames,
                                        fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
