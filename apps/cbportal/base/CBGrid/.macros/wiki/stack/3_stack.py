
def main(j, args, params, tags, tasklet):
    from JumpScale.portal.portal import exceptions
    params.result = (args.doc, args.doc)
    stackId = args.requestContext.params.get('id')

    ccl = j.clients.osis.getNamespace('cloudbroker')
    try:
        stackId = int(stackId)
    except:
        return params
        pass
    stack = ccl.stack.searchOne({'id': int(stackId)})
    if not stack:
        return params

    raise exceptions.Redirect('/cbgrid/physicalNode?id={referenceId}&gid={gid}'.format(**stack))
