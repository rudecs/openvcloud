from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    accountId = args.getTag('accountId')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['locationCode']))

    popup = Popup(id='create_space', header='Create Space', submit_url='/restmachine/cloudbroker/cloudspace/create')
    popup.addText('Name', 'name', required=True)
    popup.addText('Username to grant access', 'access', required=True)
    popup.addDropdown('Choose Location', 'location', locations)
    popup.addHiddenField('accountId', accountId)
    popup.addHiddenField('maxMemoryCapacity', 0)
    popup.addHiddenField('maxDiskCapacity', 0)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
