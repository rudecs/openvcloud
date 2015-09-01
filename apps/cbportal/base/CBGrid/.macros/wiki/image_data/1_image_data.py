
def main(j, args, params, tags, tasklet):
    import JumpScale.baselib.units

    imageid = args.getTag('id')
    if not imageid:
        out = 'Missing Image id param "id"'
        params.result = (out, args.doc)
        return params

    ccl = j.clients.osis.getNamespace('libvirt')

    if not ccl.image.exists(imageid):
        params.result = ('Image with id %s not found' % imageid, args.doc)
        return params


    imageobj = ccl.image.get(imageid)
    
    image = imageobj.dump()

    args.doc.applyTemplate(image)

    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
