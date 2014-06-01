import urlparse

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ['Id', 'Name', 'ReferenceId', 'Type', 'Description']
    fieldvalues = ["<a href='/cbgrid/stack?id=%(id)s'>%(id)s</a>", "name", 'referenceId', 'type', 'descr']
    fieldids = ['id', 'name', 'referenceId', 'type', 'descr']
    tableid = modifier.addTableForModel('cloudbroker', 'stack', fieldids, fieldnames, fieldvalues)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
