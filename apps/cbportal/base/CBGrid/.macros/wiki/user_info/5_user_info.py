def main(j, args, params, tags, tasklet):
    guid = args.getTag('guid')
    if not guid:
        args.doc.applyTemplate({})
        params.result = (args.doc, args.doc)
        return params

    if not j.apps.system.usermanager.modelUser.exists(guid):
        args.doc.applyTemplate({})
        params.result = (args.doc, args.doc)
        return params

    obj = j.apps.system.usermanager.modelUser.get(guid).dump()

    args.doc.applyTemplate(obj, True)
    params.result = (args.doc, args.doc)
    return params
