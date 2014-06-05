from JumpScale import j

descr = """
Update CloudBroker Images
"""

name = "cloudbroker_updateimages"
category = "cloudbroker"
organization = "cloudscalers"
author = "khamisr@codescalers.com"
license = "bsd"
version = "1.0"
roles = ['cloudbroker']
queue = "io"
async = True
log = True

providers = dict()

def CloudProvider(stackId):
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver
    from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
    from CloudscalerLibcloud.utils.connection import CloudBrokerConnection

    cbcl = j.core.osis.getClientForNamespace('cloudbroker')

    stack = cbcl.stack.get(stackId)
    providertype = getattr(Provider, stack.type)
    kwargs = dict()
    if stackId not in providers:
        providers[stackId] = None
        if stack.type == 'OPENSTACK':
            DriverClass = get_driver(providertype)
            args = [ stack.login, stack.passwd]
            kwargs['ex_force_auth_url'] = stack.apiUrl
            kwargs['ex_force_auth_version'] = '2.0_password'
            kwargs['ex_tenant_name'] = stack.login
            providers[stackId] = DriverClass(*args, **kwargs)
        if stack.type == 'DUMMY':
            DriverClass = get_driver(providertype)
            args = [1,]
            providers[stackId] = DriverClass(*args, **kwargs)
        if stack.type == 'LIBVIRT':
            kwargs['id'] = stack.referenceId
            kwargs['uri'] = stack.apiUrl
            prov = CSLibvirtNodeDriver(**kwargs)
            cb = CloudBrokerConnection('127.0.0.1', 9999, '1234')
            prov.set_backend(cb)
            providers[stackId] = prov
    providers[stackId].cbcl = cbcl
    return providers[stackId]

def stackImportImages(stackId):
    provider = CloudProvider(stackId)
    if not provider:
        raise RuntimeError('Provider not found')
    count = 0
    stack = provider.cbcl.stack.get(stackId)
    stack.images = []
    for pimage in provider.list_images():
        images = provider.cbcl.image.simpleSearch({'referenceId':pimage.id})
        if not images:
            image = provider.cbcl.models.image.new()
            image.name = pimage.name
            image.referenceId = pimage.id
            image.type = pimage.extra['imagetype']
            image.size = pimage.extra['size']
            image.username = pimage.extra['username']
            image.status = 'CREATED'
            image.accountId = 0
        else:
            imageid = images[0]['id']
            image = provider.cbcl.image.get(imageid)
            image.name = pimage.name
            image.referenceId = pimage.id
            image.type = pimage.extra['imagetype']
            image.size = pimage.extra['size']
            image.username = pimage.extra['username']
        count += 1
        imageid = provider.cbcl.image.set(image)[0]
        if not imageid in stack.images:
            stack.images.append(imageid)
            provider.cbcl.stack.set(stack)
    return count

def action():
    import JumpScale.grid.osis

    result = list()
    cbcl = j.core.osis.getClientForNamespace('cloudbroker')
    stacks = cbcl.stack.list()
    for stack in stacks:
        result.append(stackImportImages(stack))

    return result


