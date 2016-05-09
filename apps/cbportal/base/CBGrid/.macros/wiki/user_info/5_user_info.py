def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    guid = args.getTag('guid')
    if not guid or not guid.isdigit():
        args.doc.applyTemplate({})
        return params

    if not j.apps.system.usermanager.modelUser.exists(guid):
        args.doc.applyTemplate({})
        return params

    obj = j.apps.system.usermanager.modelUser.get(guid).dump()

    args.doc.applyTemplate(obj, True)
    return params
