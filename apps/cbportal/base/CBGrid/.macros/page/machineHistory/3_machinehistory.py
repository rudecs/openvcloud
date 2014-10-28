
def main(j, args, params, tags, tasklet):
    page = args.page
    machineId = args.getTag('machineid')
    if not machineId:
        page.addMessage('Missing machineId')
        params.result = page
        return params

    j.apps.actorsloader.getActor('cloudbroker', 'machine')
    
    history = j.apps.cloudbroker.machine.getHistory(machineId)
    if not isinstance(history, list):
        page.addMessage(history)
        params.result = page
        return params
        
    page.addMessage('HISTORY:%s' % history)

    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
