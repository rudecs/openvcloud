
def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    stackid = args.getTag('stackid')
    filters = dict()
    if stackid:
        stackid = int(stackid)
        ccl = j.clients.osis.getNamespace('cloudbroker')
        stack = ccl.stack.get(stackid)
        images = ccl.image.search({'id': {'$in': stack.images}})[1:]
        imageids = [ image['referenceId'] for image in images ]
        filters['id'] = imageids

    fieldnames = ['Name', 'Type', 'Size', 'UNCPath']
    fieldvalues = ["<a href='/cbgrid/image?id=%(id)s'>%(name)s</a>", 'type', '%(size)s GiB', 'UNCPath']
    fieldids = ['name', 'type', 'size', 'uncpath']
    tableid = modifier.addTableForModel('libvirt', 'image', fieldids, fieldnames, fieldvalues, filters)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
