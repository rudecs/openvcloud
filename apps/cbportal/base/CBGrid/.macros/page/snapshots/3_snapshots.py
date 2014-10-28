try:
    import ujson as json
except Exception:
    import json
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    if not machineId:
        page.addMessage('Missing machineId')
        params.result = page
        return params

    modifier = j.html.getPageModifierGridDataTables(page)
    j.apps.actorsloader.getActor('cloudbroker', 'machine')

    def _formatdata(snapshots):
        aaData = list()
        for snapshot in snapshots:
            epoch = j.base.time.epoch2HRDateTime(snapshot['epoch']) if not snapshot['epoch']==0 else 'N/A'
            itemdata = [snapshot['name'], epoch]
            aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    snapshots = j.apps.cloudbroker.machine.listSnapshots(machineId)
    try:
        snapshots = json.loads(snapshots)
    except Exception, e:
        page.addMessage(e)
        params.result = page
        return params
        
    snapshots = _formatdata(snapshots)

    page = args.page
    modifier = j.html.getPageModifierGridDataTables(page)

    fieldnames = ('Name', 'Take at')
    tableid = modifier.addTableFromData(snapshots, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
