from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    machineId = int(args.getTag('machineId'))
    ccl = j.clients.osis.getNamespace('cloudbroker')
    actors = j.apps.cloudbroker.iaas.cb.actors.cloudapi

    vmachine = ccl.vmachine.get(machineId)
    image = ccl.image.get(vmachine.imageId)
    bootdisks = ccl.disk.search({'id': {'$in': vmachine.disks}, 'type': 'B'})[1:]
    if len(bootdisks) != 1:
        return params
    bootdisk = bootdisks[0]
    popup = Popup(id='resizemachine', header='Resize Machine', submit_url='/restmachine/cloudbroker/machine/resize', showresponse=True)
    if not image.hotResize:
        popup.addMessage('Machine resizing will take effect on next start')
    popup.addNumber('Number of VCPUS', 'vcpus')
    popup.addNumber('Amount of memory', 'memory')
    popup.addHiddenField('machineId', machineId)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True
