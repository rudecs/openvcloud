try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    gid = args.getTag('gid')
    if not gid:
        out = 'Missing GID param "id"'
        params.result = (out, args.doc)
        return params

    gid = int(gid)
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    locations = cbclient.location.search({'gid': gid})[1:]
    if not locations:
        params.result = ('Grid with id %s not found' % id, args.doc)
        return params

    obj = locations[0]
    obj['breadcrumbname'] = obj['name']
    args.doc.applyTemplate(obj)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
