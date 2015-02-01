try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    id = args.getTag('id')
    if not id:
        out = 'Missing account id param "id"'
        params.result = (out, args.doc)
        return params
    
    id = int(id)
    cbclient = j.clients.osis.getNamespace('cloudbroker')
    sclient = j.clients.osis.getNamespace('system')

    if not cbclient.account.exists(id):
        params.result = ('Account with id %s not found' % id, args.doc)
        return params

    accountobj = cbclient.account.get(id)
    
    account = accountobj.dump()

    users = list()
    for acl in account['acl']:
        if acl['type'] == 'U':
            eusers = sclient.user.simpleSearch({'id': acl['userGroupId']})
            if eusers:
                user = eusers[0]
                user['acl'] = acl['right']
            else:
                user = dict()
                user['id'] = acl['userGroupId']
                user['emails'] = 'N/A'
            users.append(user)
    
    account['users'] = users
    args.doc.applyTemplate(account)

    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
