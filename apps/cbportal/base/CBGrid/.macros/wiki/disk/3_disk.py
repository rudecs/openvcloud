def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    diskid = args.requestContext.params.get('id')

    osiscl = j.clients.osis.getByInstance('main')
    cbosis = j.clients.osis.getNamespace('cloudbroker', osiscl)
    
    try:
        disk = cbosis.disk.get(int(diskid))
    except:
        args.doc.applyTemplate({})
        return params
    disk_data = disk.dump()
    disk_data['type'] = 'Data' if disk_data['type'] == str('D') else 'Boot'

    args.doc.applyTemplate(disk_data, False)
    return params

    