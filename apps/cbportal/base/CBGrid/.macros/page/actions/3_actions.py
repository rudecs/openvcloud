try:
    import ujson as json
except:
    import json


def main(j, args, params, tags, tasklet):
    page = args.page
    actions = args.getTag('actions')
    actiontype = args.getTag('actiontype')
    machineid = args.getTag('machineid')
    name = args.getTag('name')
    accountname = args.getTag('accountname')
    reason = args.getTag('reason')
    gid = args.getTag('gid')
    age = args.getTag('age') or '-3w'


    if not actiontype or actiontype not in ['machine', 'account', 'grid', 'computenode']:
        out = '"actiontype" param. Must be "machine", "account", "computenode" or "grid"'
        params.result = (out, args.doc)
        return params

    actionsmap = {'machine': 
                    {'start': 
                        {'Start Machine': '/restmachine/cloudapi/machines/start?machineId=%s' % machineid},
                     'stop':
                        {'Stop Machine': '/restmachine/cloudapi/machines/stop?machineId=%s' % machineid},
                     'delete':
                        {'Delete Machine': '/restmachine/cloudapi/machines/delete?machineId=%s' % machineid},
                     'snapshot':
                        {'Take a snapshot of machine': '/restmachine/cloudapi/machines/snapshot?machineId=%s&name=%s' % (machineid, name)},
                     'resume':
                        {'Resume Machine': '/restmachine/cloudapi/machines/resume?machineId=%s' % machineid},
                     'reboot':
                        {'Reboot Machine': '/restmachine/cloudapi/machines/reboot?machineId=%s' % machineid}
                    },
                  'account': 
                    {'enable': 
                        {'Enable Account': '/restmachine/cloudapi/account/enable?accountname=%s&reason=%s' % (accountname, reason)},
                     'disable':
                        {'Disable Account': '/restmachine/cloudapi/account/disable?accountname=%s&reason=%s' % (accountname, reason)},
                     'delete':
                        {'Delete Account': '/restmachine/cloudapi/account/delete?accountname=%s&reason=%s' % (accountname, reason)},
                    },
                  'grid': 
                    {'purgeLogs': 
                        {'Purge Logs': '/restmachine/cloudapi/grid/purgelogs?gid=%s&age=%s' % (gid, age)}
                    },
                  'computenode':
                    {'setStatus_enabled': 
                        {'Set Stack Status to ENABLED': '/restmachine/cloudapi/computenode/setstatus?name=%s&status=ENABLED&gid=%s' % (name, gid)},
                     'setStatus_disabled': 
                        {'Set Stack Status to DISABLED': '/restmachine/cloudapi/computenode/setstatus?name=%s&status=DISABLED&gid=%s' % (name, gid)},
                     'setStatus_offline': 
                        {'Set Stack Status to OFFLINE': '/restmachine/cloudapi/computenode/setstatus?name=%s&status=OFFLINE&gid=%s' % (name, gid)},
                     'enable': 
                        {'Enable stack': '/restmachine/cloudapi/computenode/enable?name=%s&gid=%s' % (name, gid)},
                     'disable': 
                        {'Disable stack': '/restmachine/cloudapi/computenode/disable?name=%s&gid=%s' % (name, gid)}
                    }
                  
                }

    actionoptions = dict()
    if actiontype == 'computenode' and 'setstatus' in actions:
        actions = 'setStatus_enabled,setStatus_disabled,setStatus_offline'
    for action in actions.split(','):                
        if action in actionsmap[actiontype]:
            actionoptions.update(actionsmap[actiontype].get(action))

    id = page.addComboBox(actionoptions)

    page.addJS(None, """
        $(document).ready(function() {
            $("#%s").change(function () {
                $.ajax({
                   type: "POST",
                   url: $("#%s").val(),
                });
            });
        });
        """ % (id, id))


    params.result = page

    return params


def match(j, args, params, tags, tasklet):
    return True
