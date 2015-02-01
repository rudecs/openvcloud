from JumpScale import j

descr = """
Follow up import to new machine
"""

name = "cloudbroker_import_tonewmachine"
category = "cloudbroker"
organization = "cloudscalers"
author = "hendrik@mothership1.com"
license = "bsd"
version = "1.0"
roles = []
queue = "default"
async = True



def action(name, cloudspaceId, vmexportId, sizeId, description, storageparameters):
    import JumpScale.grid.osis
    import JumpScale.grid.agentcontroller
    import JumpScale.portal
    import ujson, random
    from JumpScale.baselib.backuptools import object_store
    from JumpScale.baselib.backuptools import backup

    agentcontroller = j.clients.agentcontroller.get()
    cloudbrokermodel = j.clients.osis.getNamespace('cloudbroker')
    libvirtmodel = j.clients.osis.getNamespace('libvirt')
    system_cl = j.clients.osis.getNamespace('system')
    
    #first we need to upload the image on a correct location
    #At this moment we select a random value
    stacks = cloudbrokermodel.stack.simpleSearch({})
    if len(stacks) == 1:
        stack = stacks[0]
    else:
        stack = stacks[random.randrange(0, len(stacks)-1)]

    nodes = system_cl.node.simpleSearch({'name':stack['referenceId']})
    if len(nodes) != 1:
        raise Exception('Incorrect model structure')
    nid = nodes[0]['id']
    vmexport = cloudbrokermodel.vmexport.get(vmexportId)
    if not vmexport:
        raise Exception('Export definition with id %s not found' % vmexportId)  
    mdbucketname = storageparameters['mdbucketname']
    

    cloudspace = cloudbrokermodel.cloudspace.get(cloudspaceId)

    path = '/mnt/vmstor/templates/'
    metadata = ujson.loads(vmexport.files)
    image_name = '%s-%s.qcow2' % (vmexport.name, vmexport.id)
    args = {'path':path, 'metadata':metadata, 'storageparameters': storageparameters, 'qcow_only':True, 'filename': image_name }
    result = agentcontroller.executeJumpscript('cloudscalers', 'cloudbroker_import_onnode', args=args, nid=nid, wait=True)['result']

    image_id = vmexport.id
    imagepath = image_name
    installed_images = libvirtmodel.image.list()
    if image_id not in installed_images:
        image = dict()
        image['name'] = vmexport.name
        image['id'] = image_id
        image['UNCPath'] = imagepath
        image['type'] = 'Custom Templates'
        image['size'] = vmexport.original_size
        libvirtmodel.image.set(image)

    id = result['node_id']

    rp = libvirtmodel.resourceprovider.get(id)
    if not image_id in rp.images:
        rp.images.append(image_id)

    libvirtmodel.resourceprovider.set(rp)

    image = cloudbrokermodel.image.new()
    image.name = vmexport.name
    image.referenceId = str(image_id)
    image.type = 'Custom Templates'
    image.size = vmexport.original_size
    image.username = ""
    image.accountId = cloudspace.accountId
    image.status = 'CREATED'
    imageId = cloudbrokermodel.image.set(image)[0]

    stack = cloudbrokermodel.stack.get(stack['id'])
    stack.images.append(imageId)
    cloudbrokermodel.stack.set(stack)
    disksize = vmexport.original_size
    
    portalcfgpath = j.system.fs.joinPaths(j.dirs.baseDir, 'apps', 'cloudbroker', 'cfg', 'portal')
    portalcfg = j.config.getConfig(portalcfgpath).get('main', {})
    port = int(portalcfg.get('webserverport', 9999))
    secret = portalcfg.get('secret')
    cl = j.clients.portal.get('127.0.0.1', port, secret)
    cl.getActor('cloudapi', 'machines')

    machineid = j.apps.cloudapi.machines.create(cloudspaceId, name, description, sizeId, imageId, disksize)


    return machineid