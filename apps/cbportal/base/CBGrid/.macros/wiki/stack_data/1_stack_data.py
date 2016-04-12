
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units

    stid = args.getTag('id')
    if not stid:
        args.doc.applyTemplate({})
        params.result = (args.doc, args.doc)
        return params

    stid = int(stid)
    ccl = j.clients.osis.getNamespace('cloudbroker')

    if not ccl.stack.exists(stid):
        params.result = ('Stack with id %s not found' % stid, args.doc)
        return params


    stack = ccl.stack.get(stid).dump()
    args.doc.applyTemplate(stack, True)
    params.result = (args.doc, args.doc)

    return params

def match(j, args, params, tags, tasklet):
    return True
