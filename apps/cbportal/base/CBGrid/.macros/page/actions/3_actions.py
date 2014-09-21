try:
    import ujson as json
except:
    import json


def main(j, args, params, tags, tasklet):
    page = args.page
    machineid = args.getTag('machineid')
    name = args.getTag('name')
    actions = args.getTag('actions')

    actionsmap = {'start': 
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
                    {'Reboot Machine': '/restmachine/cloudapi/machines/reboot?machineId=%s' % machineid},
                }

    actionoptions = dict()
    for action in actions.split(','):
        if action in actionsmap:
            actionoptions.update(actionsmap[action])

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
