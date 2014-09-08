
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units

    imageid = args.getTag('id')
    if not imageid:
        out = 'Missing Image id param "id"'
        params.result = (out, args.doc)
        return params

    ccl = j.core.osis.getClientForNamespace('libvirt')

    if not ccl.image.exists(imageid):
        params.result = ('Image with id %s not found' % imageid, args.doc)
        return params

    def objFetchManipulate(id):
        return ccl.image.get(int(imageid)).dump()

    push2doc=j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
