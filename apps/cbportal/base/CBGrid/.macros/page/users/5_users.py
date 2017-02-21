
def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    filters = dict()

    for tag, val in args.tags.tags.iteritems():
        val = args.getTag(tag)
        if tag == 'userdetails':
            continue
        if isinstance(val, list):
            val = ', '.join(val)
        filters[tag] = val

    fields = [
        {'id': 'id',
         'name': 'ID',
         'value': "[%(id)s|/cbgrid/user?id=%(id)s]"},
        {'id': 'emails',
         'name': 'Email',
         'value': 'emails'},
        {'id': 'groups',
         'name': 'Groups',
         'value': 'groups',
         'sortable': False}
    ]

    tableid = modifier.addTableFromModel('system', 'user', fields, filters, selectable='rows')
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 1, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
