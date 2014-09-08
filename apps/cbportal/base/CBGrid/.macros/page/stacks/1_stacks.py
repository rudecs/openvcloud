import urlparse

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    imageid = args.getTag("imageid")
    filters = dict()

    if imageid:
        imageid = int(imageid)
        ccl = j.core.osis.getClientForNamespace('cloudbroker')
        images = ccl.image.simpleSearch({'referenceId': imageid})
        if images:
            filters['images'] = images[0]['id']

    fieldnames = ['Id', 'Name', 'ReferenceId', 'Type', 'Description']
    fieldvalues = ["<a href='/cbgrid/stack?id=%(id)s'>%(id)s</a>", "name", 'referenceId', 'type', 'descr']
    fieldids = ['id', 'name', 'referenceId', 'type', 'descr']
    tableid = modifier.addTableForModel('cloudbroker', 'stack', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
