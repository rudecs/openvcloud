from JumpScale.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['gid']))

    popup = Popup(id='createcdrom', header='Create CD-ROM Image',
                  submit_url='/restmachine/cloudbroker/image/createCDROMImage',
                  reload_on_success=False)
    popup.addText('Name', 'name', required=True)
    popup.addText('URL of CD-ROM image to import', 'url', required=True)
    popup.addText('AccountId optional if you want to make the image for this account only', 'accountId')
    popup.addDropdown('Choose Location', 'gid', locations)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
