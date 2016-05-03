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
    accountdict['maxMemoryCapacity'] = "%s" % accountobj.resourceLimits['CU_M'] \
        if 'CU_M' in accountobj.resourceLimits else -1
    accountdict['maxVDiskCapacity'] = "%s" % accountobj.resourceLimits['CU_D'] \
        if 'CU_D' in accountobj.resourceLimits else -1
    accountdict['maxCPUCapacity'] = accountobj.resourceLimits['CU_C'] \
        if 'CU_C' in accountobj.resourceLimits else -1
    accountdict['maxNASCapacity'] = "%s" % accountobj.resourceLimits['CU_S'] \
        if 'CU_S' in accountobj.resourceLimits else -1
    accountdict['maxArchiveCapacity'] = "%s" % accountobj.resourceLimits['CU_A'] \
        if 'CU_A' in accountobj.resourceLimits else -1
    accountdict['maxNetworkOptTransfer'] = "%s" % accountobj.resourceLimits['CU_NO'] \
        if 'CU_NO' in accountobj.resourceLimits else -1
    accountdict['maxNetworkPeerTransfer'] = "%s" % accountobj.resourceLimits['CU_NP'] \
        if 'CU_NP' in accountobj.resourceLimits else -1
    accountdict['maxNumPublicIP'] = accountobj.resourceLimits['CU_I'] \
        if 'CU_I' in accountobj.resourceLimits else -1

    args.doc.applyTemplate(accountdict, True)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
