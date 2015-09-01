from JumpScale.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['locationCode']))

    popup = Popup(id='createaccount', header='Create Account', submit_url='/restmachine/cloudbroker/account/create')
    popup.addText('Name', 'name', required=True, placeholder='Account Name')
    popup.addText('Username', 'username', required=True,
                  placeholder='Owner of account, will be created if does not exist')
    popup.addText('Email Address', 'emailaddress', required=False,
                  placeholder='User email, only required if username does not exist')
    popup.addDropdown('Choose Location', 'location', locations)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
