import urlparse

def main(j, args, params, tags, tasklet):

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    def apiUrl(row, field):
        apiurl = row[field]
        return urlparse.urlparse(apiurl).netloc

    fieldnames = ['Name', 'API IP', 'Type', 'Description']
    fieldvalues = ["<a href='/cbgrid/stack?id=%(id)s'>%(name)s</a>", apiUrl, 'type', 'descr']
    fieldids = ['name', 'apiUrl', 'type', 'descr']
    tableid = modifier.addTableForModel('cloudbroker', 'stack', fieldids, fieldnames, fieldvalues)
    modifier.addSearchOptions('#%s' % tableid)

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
