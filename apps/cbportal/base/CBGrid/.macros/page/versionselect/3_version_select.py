import requests
import re
from JumpScale.portal.docgenerator.popup import Popup
from pkg_resources import parse_version
def main(j, args, params, tags, tasklet):
    scl = j.clients.osis.getNamespace('system')
    params.result = page = args.page
    contents = requests.get('https://api.github.com/repos/0-complexity/home/contents/manifests').json()
    current_version = scl.version.searchOne({'status': 'CURRENT'})['name']
    versions = []
    for file in contents:
        if re.search("^(\d+\.)?(\d+\.)?(\d+)", file['name']):
            version = file['name'].split('.yml')[0]
            if parse_version(version) > parse_version(current_version):
                versions.append((version, version))

    popup = Popup(id='updateenv', header='Update environment',
                  submit_url='/restmachine/cloudbroker/grid/upgrade')
    popup.addDropdown('Choose version to update', 'version', versions)
    popup.write_html(page)
    return params
