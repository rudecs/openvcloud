def main(j, args, params, tags, tasklet):
    params.result = (args.doc, args.doc)

    def _get_data(data):
        return [val['id'] for val in data]

    ccl = j.clients.osis.getNamespace('cloudbroker')
    cloudspaceIds = _get_data(ccl.cloudspace.search({'$fields': ['id'], '$query': {'status': 'DELETED'}})[1:])
    machineIds = _get_data(ccl.vmachine.search({'$fields': ['id'], '$query': {'status': 'DELETED'}})[1:])
    BdiskIds = _get_data(ccl.disk.search({'$fields': ['id'], '$query': {'status': 'TOBEDELETED', 'type': {'$in': ['B', 'D']}}})[1:])
    CdiskIds = _get_data(ccl.disk.search({'$fields': ['id'], '$query': {'status': 'TOBEDELETED', 'type': 'C'}})[1:])
    imageIds = _get_data(ccl.image.search({'$fields': ['id'], '$query': {'status': 'DELETED'}})[1:])
    accountIds = _get_data(ccl.account.search({'$fields': ['id'], '$query': {'status': 'DELETED'}})[1:])

    obj = {
        'cloudspaceIds': cloudspaceIds,
        'machineIds': machineIds,
        'BdiskIds': BdiskIds,
        'CdiskIds': CdiskIds,
        'imageIds': imageIds,
        'accountIds': accountIds
    }

    args.doc.applyTemplate(obj, False)
    return params