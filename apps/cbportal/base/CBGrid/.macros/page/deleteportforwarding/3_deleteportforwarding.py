from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    machineId = int(args.getTag('machineId'))
    scl = j.clients.osis.getNamespace('cloudbroker')
    actors = j.apps.cloudbroker.iaas.cb.actors.cloudapi

    machine = scl.vmachine.get(machineId)
    portforwards = actors.portforwarding.list(cloudspaceid=machine.cloudspaceId, machineId=machineId)
    rules = []
    for portforward in portforwards:
        rules.append(("%(publicIp)s:%(publicPort)s -> %(localIp)s:%(localPort)s %(protocol)s" % portforward,
                      portforward['id']))

    popup = Popup(id='deleteportforwarding', header='Delete Portforwarding', submit_url='/restmachine/cloudbroker/machine/deletePortForward')
    popup.addDropdown('Choose Portforward', 'ruleId', rules)
    popup.addText('Reason', 'reason')
    popup.addHiddenField('machineId', machineId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
