from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    machineId = int(args.getTag('machineId'))
    accountName = args.getTag('accountName')
    scl = j.clients.osis.getForNamespace('cloudbroker')

    vmachine = scl.vmachine.get(machineId)
    cloudspace = scl.cloudspace.get(vmachine.cloudspaceId)
    stacks = scl.stack.search({'status': 'ENABLED', 'gid': cloudspace.gid, 'images': vmachine.imageId})[1:]
    cpu_nodes = [(stack['name'], stack['id']) for stack in stacks if vmachine.stackId != stack['id']]

    popup = Popup(id='movemachine', header='Move machine to another CPU node', submit_url='/restmachine/cloudbroker/machine/moveToDifferentComputeNode')
    popup.addDropdown('Target CPU Node', 'targetStackId', cpu_nodes, required=True)
    popup.addDropdown('With Snapshots', 'withSnapshots', [('Yes', True), ('No', False)])
    popup.addText('Reason', 'reason', required=True)
    popup.addHiddenField('machineId', machineId)
    popup.addHiddenField('accountName', accountName)
    popup.write_html(page)

    return params

def match(j, args, params, tags, tasklet):
    return True
