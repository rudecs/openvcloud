try:
    import ujson as json
except:
    import json

def main(j, args, params, tags, tasklet):

    params.result = (args.doc, args.doc)
    gid = args.getTag('gid')
    if not gid or not gid.isdigit():
        args.doc.applyTemplate({})
        return params

    gid = int(gid)
    cbclient = j.clients.osis.getNamespace('cloudbroker')

    locations = cbclient.location.search({'gid': gid})[1:]
    if not locations:
        args.doc.applyTemplate({'gid': None}, True)
        return params

    obj = locations[0]
    args.doc.applyTemplate(obj, True)
    return params

def match(j, args, params, tags, tasklet):
    return True
