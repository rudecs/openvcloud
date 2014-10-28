
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    if not machineId:
        page.addMessage('Missing machineId')
        params.result = page
        return params

    modifier = j.html.getPageModifierGridDataTables(page)
    j.apps.actorsloader.getActor('cloudbroker', 'machine')

    def _formatdata(portforwards):
        aaData = list()
        for portforward in portforwards:
            for field in ['protocol', 'fromAddr', 'fromPort', 'toAddr', 'toPort']:
                portforward[field] = j.tools.text.toStr(portforward[field])
            itemdata = [portforward['protocol'], '%s:%s' % (portforward['fromAddr'], portforward['fromPort']), '%s:%s' % (portforward['toAddr'], portforward['toPort'])]
            aaData.append(itemdata)
        aaData = str(aaData)
        return aaData.replace('[[', '[ [').replace(']]', '] ]')

    portforwards = j.apps.cloudbroker.machine.listPortForwards(machineId)
    if not isinstance(portforwards, list):
        page.addMessage(portforwards)
        params.result = page
        return params
        
    portforwards = _formatdata(portforwards)

    fieldnames = ('Protocol', 'From', 'To')
    tableid = modifier.addTableFromData(portforwards, fieldnames)

    modifier.addSearchOptions('#%s' % tableid)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
