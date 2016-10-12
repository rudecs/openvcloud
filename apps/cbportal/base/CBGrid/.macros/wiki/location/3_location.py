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

    unused_sizes = list()
    for size in cbclient.size.search({})[1:]:
        if cbclient.vmachine.count({"sizeId": size["id"]}) == 0:
            unused_sizes.append(size["id"])

    locations[0]["unused_sizes"] = unused_sizes
    obj = locations[0]
    args.doc.applyTemplate(obj, True)
    return params

def match(j, args, params, tags, tasklet):
    return True
