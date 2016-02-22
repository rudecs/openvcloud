from JumpScale.portal.docgenerator.popup import Popup

def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    accountId = args.getTag('accountId')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    locations = list()
    for location in ccl.location.search({})[1:]:
        locations.append((location['name'], location['locationCode']))

    # Placeholder that -1 means no limits are set on the cloud unit
    culimitplaceholder = 'set to -1 if no limits should be set'
    popup = Popup(id='create_space', header='Create Cloud Space', submit_url='/restmachine/cloudbroker/cloudspace/create')
    popup.addText('Name', 'name', required=True)
    popup.addText('Username to grant access', 'access', required=True)
    popup.addDropdown('Choose Location', 'location', locations)
    popup.addText('Max Memory Capacity (GB)', 'maxMemoryCapacity', placeholder=culimitplaceholder, type='float')
    popup.addText('Max VDisk Capacity (GB)', 'maxVDiskCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of CPU Cores', 'maxCPUCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Primary Storage(NAS) Capacity (TB)', 'maxNASCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Secondary Storage(Archive) Capacity (TB)', 'maxArchiveCapacity', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Network Transfer In Operator (GB)', 'maxNetworkOptTransfer', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Network Transfer Peering (GB)', 'maxNetworkPeerTransfer', placeholder=culimitplaceholder, type='number')
    popup.addText('Max Number of Public IP Addresses', 'maxNumPublicIP', placeholder=culimitplaceholder, type='number')
    popup.addHiddenField('accountId', accountId)
    popup.write_html(page)
    return params


def match(j, args, params, tags, tasklet):
    return True
