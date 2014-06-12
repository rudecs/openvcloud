from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_export"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue='default'
async = True



def action(path, name, machineId,storageparameters,nid,backup_type):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import ujson


    agentcontroller = j.clients.agentcontroller.get()
    args = {'path':path, 'name':name, 'storageparameters': storageparameters}

    if backup_type == 'raw':
        result = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_backup_create_raw', args=args, nid=nid, wait=True)['result']
    elif backup_type == 'condensed':
        result = agentcontroller.executeJumpScript('cloudscalers', 'cloudbroker_backup_create_condensed', args=args, nid=nid, wait=True)['result']
    else:
        raise 'Incorrect backup type'


    cloudbrokermodel = j.core.osis.getClientForNamespace('cloudbroker')
    vm = cloudbrokermodel.vmachine.get(machineId)
    vmobject = ujson.dumps(vm.obj2dict())

    #save config in model

    vmexport = cloudbrokermodel.vmexport.new()
    vmexport.machineId = machineId
    vmexport.type = backup_type
    if storageparameters['storage_type'] == 'S3':
        vmexport.bucket = storageparameters['bucket']
        vmexport.server = storageparameters['host']
    vmexport.storagetype = storageparameters['storage_type']
    if 'size' in result:
        vmexport.size = result['size']
    vmexport.timestamp = int(result['timestamp'])
    vmexport.config = vmobject
    vmexport.files = ujson.dumps(result['files'])

    export_id = cloudbrokermodel.vmexport.set(vmexport)
    return export_id

