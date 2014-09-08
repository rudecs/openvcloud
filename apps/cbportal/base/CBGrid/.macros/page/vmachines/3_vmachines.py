import datetime

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    stackid = args.getTag("stackid")
    cloudspaceId = args.getTag("cloudspaceid")
    filters = dict()
    nativequery = None

    if stackid:
        stackid = int(stackid)
        filters['stackId'] = stackid
        ccl = j.core.osis.getClientForNamespace('cloudbroker')
        location = j.application.config.get('cloudbroker.where_am_i')
        spaces = [ x['id'] for x in ccl.cloudspace.simpleSearch({'location': location}) ]
        nativequery = {'query': {'bool': {'must': [{'terms': {'cloudspaceId': spaces}}]}}}
    if cloudspaceId:
        filters['cloudspaceId'] = cloudspaceId

    fieldnames = ['Name', 'Status', 'Host Name', 'Created at', 'Cloud Space', 'Stack']

    def makeTime(row, field):
        time = datetime.datetime.fromtimestamp(row[field]).strftime('%m-%d %H:%M:%S') or ''
        return time

    def stackLinkify(row, field):
        return '[%s|stack?id=%s]' % (row[field], row[field])

    def nameLinkify(row, field):
        return '[%s|vmachine?id=%s]' % (row[field], row['id'])

    def spaceLinkify(row, field):
        return '[%s|cloudspace?id=%s]' % (row[field], row[field])

    fieldids = ['name', 'status', 'hostName', 'creationTime', 'cloudspaceId', 'stackId']
    fieldvalues = [nameLinkify, 'status', 'hostName', makeTime, spaceLinkify, stackLinkify]
    tableid = modifier.addTableForModel('cloudbroker', 'vmachine', fieldids, fieldnames, fieldvalues, filters, nativequery)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
