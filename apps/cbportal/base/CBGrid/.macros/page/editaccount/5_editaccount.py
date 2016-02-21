from JumpScale.portal.docgenerator.popup import Popup


def main(j, args, params, tags, tasklet):
    params.result = page = args.page
    accountId = int(args.getTag('accountId'))
    ccl = j.clients.osis.getNamespace('cloudbroker')
    accountobj = ccl.account.get(accountId)

    popup = Popup(id='editaccount', header='Edit Account',
                  submit_url='/restmachine/cloudbroker/account/update', clearForm=False)

    # Placeholder that -1 means that no limits are set on the cloud unit
    culimitplaceholder = 'set to -1 if no limits should be set'
    popup.addText('Name', 'name', value=accountobj.name)
    popup.addText('Max Memory Capacity (GB)', 'maxMemoryCapacity', placeholder=culimitplaceholder, type='float',
                  value=accountobj.resourceLimits['CU_M'] if 'CU_M' in accountobj.resourceLimits else -1)
    popup.addText('Max VDisk Capacity (GB)', 'maxVDiskCapacity', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_D'] if 'CU_D' in accountobj.resourceLimits else -1)
    popup.addText('Max Number of CPU Cores', 'maxCPUCapacity', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_C'] if 'CU_C' in accountobj.resourceLimits else -1)
    popup.addText('Max Primary Storage(NAS) Capacity (TB)', 'maxNASCapacity', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_S'] if 'CU_S' in accountobj.resourceLimits else -1)
    popup.addText('Max Secondary Storage(Archive) Capacity (TB)', 'maxArchiveCapacity', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_A'] if 'CU_A' in accountobj.resourceLimits else -1)
    popup.addText('Max Network Transfer In Operator (GB)', 'maxNetworkOptTransfer', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_NO'] if 'CU_NO' in accountobj.resourceLimits else -1)
    popup.addText('Max Network Transfer Peering (GB)', 'maxNetworkPeerTransfer', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_NP'] if 'CU_NP' in accountobj.resourceLimits else -1)
    popup.addText('Max Number of Public IP Addresses', 'maxNumPublicIP', placeholder=culimitplaceholder, type='number',
                  value=accountobj.resourceLimits['CU_I'] if 'CU_I' in accountobj.resourceLimits else -1)
    popup.addHiddenField('accountId', accountobj.id)
    popup.write_html(page)

    return params


def match(j, args, params, tags, tasklet):
    return True

