import datetime
import json

def main(j, args, params, tags, tasklet):
    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)
    stackid = args.getTag("stackid")
    cloudspaceId = args.getTag("cloudspaceid")
    imageid = args.getTag('imageid')
    gid = args.getTag('gid')
    filters = dict()
    filters['status'] = ['RUNNING', 'HALTED', 'PAUSED']
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
        stacks = ccl.stack.simpleSearch({'gid':gid})
        stacksids = [ stack['id'] for stack in stacks ]
        filters['stackId'] = stacksids

    fieldnames = ['Name', 'Host Name' ,'Status', 'Created at', 'Cloud Space', 'CPU Node']

    def _formatData():
        res = []
        cbcl = j.clients.osis.getNamespace('cloudbroker')
        for vmid in cbcl.vmachine.list():
            vm = cbcl.vmachine.get(vmid)
            name = '<a href="vmachine?id=%s">%s</a>' % (vm.id, vm.name)
            csname = cbcl.cloudspace.get(int(vm.cloudspaceId)).name
            cloudspace = '<a href="cloudspace?id=%s">%s</a>' % (vm.cloudspaceId,csname)
            stack = ''
            if vm.stackId:
                stack = '<a href="stack?id=%s">%s</a>' % (vm.stackId, vm.stackId)
            time = '<div class="jstimestamp" data-ts="%s"></div>' % vm.creationTime
            res.append([name, vm.hostName, vm.status, time, cloudspace, stack])
        return json.dumps(res)
    
    fieldvalues = _formatData()
    tableid = modifier.addTableFromData(fieldvalues, fieldnames)
    modifier.addSearchOptions('#%s' % tableid)
    modifier.addSorting('#%s' % tableid, 0, 'desc')

    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
