from JumpScale.portal.docgenerator.popup import Popup
from collections import OrderedDict

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    gid = args.getTag('gid')
    options = OrderedDict({
        'CPU Nodes': 'cpunode',
        'Storage Nodes': 'storagenode',
        'CPU and Storage Nodes': 'both'
    })

    popup = Popup(id='execute_script', header='Execute Script', submit_url='/restmachine/cloudbroker/grid/executeMaintenanceScript')
    popup.addDropdown('Select which type of nodes you want to execute this one', 'nodestype', options.iteritems())
    popup.addTextArea('Script', 'script', placeholder='Enter script here', rows=10)
    popup.addHiddenField('gid', gid)
    popup.write_html(page)
    params.result = page
    return params


def match(j, args, params, tags, tasklet):
    return True
