from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    referenceId = args.getTag('imageId')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    images = ccl.image.search({'referenceId': referenceId})[1:]
    if images:
        image = images[0]
    else:
        image = {'id': None}

    popup = Popup(id='image_update_cpu_nodes', header='Change CPU Nodes for Image', submit_url='/restmachine/cloudbroker/image/updateNodes')

    options = list()
    for stack in ccl.stack.search({})[1:]:
        available = image['id'] in stack.get('images', [])
        options.append((stack['name'], stack['id'], available))

    popup.addCheckboxes('Select Stacks', 'enabledStacks', options)
    popup.addHiddenField('imageId', referenceId)
    popup.write_html(page)

    return params
