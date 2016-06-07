
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units

    params.result = (args.doc, args.doc)
    stid = args.getTag('id')
    if not stid or not stid.isdigit():
        args.doc.applyTemplate({})
        return params

    stid = int(stid)
    ccl = j.clients.osis.getNamespace('cloudbroker')

    if not ccl.stack.exists(stid):
        args.doc.applyTemplate({'id': None}, True)
        return params


    stack = ccl.stack.get(stid).dump()
    stack['eco'] = stack['eco'] and stack['eco'].replace('-', '')
    args.doc.applyTemplate(stack, True)

    return params

def match(j, args, params, tags, tasklet):
    return True
