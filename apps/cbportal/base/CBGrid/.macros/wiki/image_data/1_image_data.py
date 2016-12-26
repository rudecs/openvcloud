def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    imageid = args.requestContext.params.get('id')
    if not imageid:
        args.doc.applyTemplate({})
        return params
    lcl = j.clients.osis.getNamespace('libvirt')

    if not lcl.image.exists(imageid):
        args.doc.applyTemplate({'imageid': None}, True)
        return params

    imageobj = lcl.image.get(imageid)
    image = imageobj.dump()

    args.doc.applyTemplate(image, True)

    return params


def match(j, args, params, tags, tasklet):
    return True
