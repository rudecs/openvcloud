from JumpScale.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['gid']))

    popup = Popup(id='createimage', header='Create Image',
                  submit_url='/restmachine/cloudbroker/image/createImage',
                  reload_on_success=False)
    popup.addText('Name', 'name', required=True)
    popup.addText('URL of image to import', 'url', required=True)
    popup.addDropdown('Choose Location', 'gid', locations)
    imagetypes = [
            ('Linux', 'Linux'),
            ('Windows', 'Windows'),
            ('Other', 'Other'),
    ]
    boottype = [
            ('BIOS', 'bios'),
            ('UEFI', 'uefi'),
    ]
    popup.addDropdown('Choose Type', 'imagetype', imagetypes)
    popup.addDropdown('Boot Type', 'boottype', boottype)
    popup.addText('Username for the image leave empty when the image is cloud-init enabled', 'username')
    popup.addText('Password for the image leave empty when the image is cloud-init enabled', 'password')
    popup.addText('AccountId optional if you want to make the image for this account only', 'accountId')
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
