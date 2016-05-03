try:
    import ujson as json
except:
    import json


def generateUsersList(sclient, cloudspacedict):
    """
    Generate the list of users that have ACEs on the account

    :param sclient: osis client for system model
    :param cloudspacedict: dict with the cloudspace data
    :return: list of users have access to cloudspace
    """
    users = list()
    for acl in cloudspacedict['acl']:
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
    vcl = j.clients.osis.getNamespace('vfw')

    if not cbclient.cloudspace.exists(id):
        params.result = ('CloudSpace with id %s not found' % id, args.doc)
        return params

    cloudspaceobj = cbclient.cloudspace.get(id)

    cloudspacedict = cloudspaceobj.dump()

    accountid = cloudspacedict['accountId']
    account = cbclient.account.get(accountid).dump() if cbclient.account.exists(accountid) else {'name':'N/A'}
    cloudspacedict['accountname'] = account['name']

    # Resource limits
    cloudspacedict['maxMemoryCapacity'] = "%s" % cloudspaceobj.resourceLimits['CU_M'] \
        if 'CU_M' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxVDiskCapacity'] = "%s" % cloudspaceobj.resourceLimits['CU_D'] \
        if 'CU_D' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxCPUCapacity'] = cloudspaceobj.resourceLimits['CU_C'] \
        if 'CU_C' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxNASCapacity'] = "%s" % cloudspaceobj.resourceLimits['CU_S'] \
        if 'CU_S' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxArchiveCapacity'] = "%s" % cloudspaceobj.resourceLimits['CU_A'] \
        if 'CU_A' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxNetworkOptTransfer'] = "%s" % cloudspaceobj.resourceLimits['CU_NO'] \
        if 'CU_NO' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxNetworkPeerTransfer'] = "%s" % cloudspaceobj.resourceLimits['CU_NP'] \
        if 'CU_NP' in cloudspaceobj.resourceLimits else -1
    cloudspacedict['maxNumPublicIP'] = cloudspaceobj.resourceLimits['CU_I'] \
        if 'CU_I' in cloudspaceobj.resourceLimits else -1

    vfwkey = "%(gid)s_%(networkId)s" % (cloudspacedict)
    if vcl.virtualfirewall.exists(vfwkey):
        network = vcl.virtualfirewall.get(vfwkey).dump()
        cloudspacedict['network'] = network
    else:
        if cloudspacedict['networkId']:
            cloudspacedict['networkid'] = cloudspacedict['networkId']
        else:
            cloudspacedict['networkid'] = 'N/A'
        cloudspacedict['network'] = {'tcpForwardRules': []}

    cloudspacedict['users'] = generateUsersList(sclient, cloudspacedict)
    args.doc.applyTemplate(cloudspacedict, True)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
