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

    params.result = (args.doc, args.doc)
    id = args.getTag('id')
    try:
        id = int(id)
    except:
        pass
    if not isinstance(id, int):
        args.doc.applyTemplate({})
        return params

    cbclient = j.clients.osis.getNamespace('cloudbroker')
    sclient = j.clients.osis.getNamespace('system')
    vcl = j.clients.osis.getNamespace('vfw')

    if not cbclient.cloudspace.exists(id):
        args.doc.applyTemplate({'id': None}, False)
        return params

    cloudspaceobj = cbclient.cloudspace.get(id)

    cloudspacedict = cloudspaceobj.dump()

    accountid = cloudspacedict['accountId']
    account = cbclient.account.get(accountid).dump() if cbclient.account.exists(accountid) else {'name':'N/A'}
    cloudspacedict['accountname'] = account['name']

    # Resource limits

    j.apps.cloudbroker.account.cb.fillResourceLimits(cloudspaceobj.resourceLimits)
    cloudspacedict['reslimits'] = cloudspaceobj.resourceLimits

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
    args.doc.applyTemplate(cloudspacedict, False)
    return params

def match(j, args, params, tags, tasklet):
    return True
