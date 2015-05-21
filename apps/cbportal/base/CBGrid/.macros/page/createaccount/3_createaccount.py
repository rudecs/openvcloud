from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['locationCode']))

    popup = Popup(id='createaccount', header='Create Account', submit_url='/restmachine/cloudbroker/account/create')
    popup.addText('Username', 'username', required=True)
    popup.addText('Display Name', 'name', required=True)
    popup.addText('Email Address', 'emailaddress', required=True)
    popup.addText('Password (min 6 characters)', 'password', required=True, type='password')
    popup.addDropdown('Choose Location', 'location', locations)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
