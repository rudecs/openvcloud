def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)
    diskid = args.requestContext.params.get('id')

    osiscl = j.clients.osis.getByInstance('main')
    cbosis = j.clients.osis.getNamespace('cloudbroker', osiscl)

    def prettify(iotune):
        result = {}
        for key in iotune.keys():
            orig = key
            if 'max' in key:
                key = 'max ' + key.replace('_max', '')
            key = key.capitalize().replace('_', ' ')
            index = key.find('sec')
            key = key[:index] + 'per ' + key[index:]
            result[key] = iotune[orig]
        return result

    try:
        disk = cbosis.disk.get(int(diskid))
    except:
        args.doc.applyTemplate({})
        return params
    disk_data = disk.dump()
    disk_data['type'] = 'Data' if disk_data['type'] == str('D') else 'Boot'
    volume = j.apps.cloudapi.disks.getStorageVolume(disk, None)
    disk_data['edgehost'] = volume.edgehost
    disk_data['edgeport'] = volume.edgeport
    disk_data['vdiskguid'] = volume.vdiskguid
    disk_data['edgename'] = volume.name
    disk_data['devicename'] = volume.dev

    if disk_data['iotune']:
        disk_data['iotune'] = prettify(disk_data['iotune'])
    args.doc.applyTemplate(disk_data, False)
    return params

    
