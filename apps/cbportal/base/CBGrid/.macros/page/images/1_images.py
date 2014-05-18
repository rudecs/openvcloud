import urlparse

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    stackid = args.getTag('stackid')
    nativequery = None
    if stackid:
        ccl = j.core.osis.getClientForNamespace('cloudbroker')
        stack = ccl.stack.get(stackid)
        query = {'query': {'bool': {'must': [{'terms': {'id': stack.images}}]}}}
        images = ccl.image.simpleSearch({}, nativequery=query)
        imageids = [ image['referenceId'] for image in images ]
        nativequery = {'query': {'bool': {'must': [{'terms': {'id': imageids}}]}}}

    fieldnames = ['Name', 'Type', 'Size', 'UNCPath']
    fieldvalues = ["<a href='/cbgrid/image?id=%(id)s'>%(name)s</a>", 'type', '%(size)s GiB', 'UNCPath']
    fieldids = ['name', 'type', 'size', 'uncpath']
    tableid = modifier.addTableForModel('libvirt', 'image', fieldids, fieldnames, fieldvalues, nativequery=nativequery)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
