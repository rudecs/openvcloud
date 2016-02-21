try:
    import ujson as json
except:
    import json


def generateUsersList(sclient, accountdict):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param accountdict: dict with the account data
    :return: list of users have access to account
    """
    users = list()
    for acl in accountdict['acl']:
        if acl['type'] == 'U':
            eusers = sclient.user.simpleSearch({'id': acl['userGroupId']})
            if eusers:
                user = eusers[0]
                user['userstatus'] = acl['status']
            elif acl['status'] == 'INVITED':
                user = dict()
                user['id'] = acl['userGroupId']
                user['emails'] = [acl['userGroupId']]
                user['userstatus'] = acl['status']
            else:
                user = dict()
                user['id'] = acl['userGroupId']
                user['emails'] = ['N/A']
                user['userstatus'] = 'N/A'
            user['acl'] = acl['right']
            users.append(user)
    return users


def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        args.doc.applyTemplate({})
        params.result = (args.doc, args.doc)
        return params
    
    id = int(id)
    cbclient = j.clients.osis.getNamespace('cloudbroker')
    sclient = j.clients.osis.getNamespace('system')

    if not cbclient.account.exists(id):
        params.result = ('Account with id %s not found' % id, args.doc)
        return params

    accountobj = cbclient.account.get(id)
    
    accountdict = accountobj.dump()

    accountdict['users'] = generateUsersList(sclient, accountdict)

    balances = cbclient.credittransaction.search({'accountId': id})[1:]
    balance = 0
    if balances:
        balance = sum([bal['amount'] for bal in balances])
    accountdict['balance'] = balance
    accountdict['maxMemoryCapacity'] = "%s GB" % accountobj.resourceLimits['CU_M'] if accountobj.resourceLimits['CU_M'] != -1 else "Unlimited"
    accountdict['maxVDiskCapacity'] = "%s GB" % accountobj.resourceLimits['CU_D'] if accountobj.resourceLimits['CU_D'] != -1 else "Unlimited"
    accountdict['maxCPUCapacity'] = accountobj.resourceLimits['CU_C'] if accountobj.resourceLimits['CU_C'] != -1 else "Unlimited"
    accountdict['maxNASCapacity'] = "%s TB" % accountobj.resourceLimits['CU_S'] if accountobj.resourceLimits['CU_S'] != -1 else "Unlimited"
    accountdict['maxArchiveCapacity'] = "%s TB" % accountobj.resourceLimits['CU_A'] if accountobj.resourceLimits['CU_A'] != -1 else "Unlimited"
    accountdict['maxNetworkOptTransfer'] = "%s GB" % accountobj.resourceLimits['CU_NO'] if accountobj.resourceLimits['CU_NO'] != -1 else "Unlimited"
    accountdict['maxNetworkPeerTransfer'] = "%s GB" % accountobj.resourceLimits['CU_NP'] if accountobj.resourceLimits['CU_NP'] != -1 else "Unlimited"
    accountdict['maxNumPublicIP'] = accountobj.resourceLimits['CU_I'] if accountobj.resourceLimits['CU_I'] != -1 else "Unlimited"

    args.doc.applyTemplate(accountdict)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
