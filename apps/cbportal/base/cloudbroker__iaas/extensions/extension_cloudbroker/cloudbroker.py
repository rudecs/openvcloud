from JumpScale import j
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver
from CloudscalerLibcloud.utils.connection import CloudBrokerConnection
import JumpScale.grid.osis


class CloudProvider(object):
    providers = dict()
    def __init__(self, stackId):
        cbcl = j.core.osis.getClientForNamespace('cloudbroker')
        cbip = j.application.config.get('cloudbroker.ip')
        cbport = j.application.config.get('cloudbroker.port')
        cbsecret = j.application.config.get('cloudbroker.secret')

        stack = cbcl.stack.get(stackId)
        providertype = getattr(Provider, stack.type)
        kwargs = dict()
        if stackId not in CloudProvider.providers:
            CloudProvider.providers[stackId] = None
            if stack.type == 'OPENSTACK':
                DriverClass = get_driver(providertype)
                args = [ stack.login, stack.passwd]
                kwargs['ex_force_auth_url'] = stack.apiUrl
                kwargs['ex_force_auth_version'] = '2.0_password'
                kwargs['ex_tenant_name'] = stack.login
                CloudProvider.providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'DUMMY':
                DriverClass = get_driver(providertype)
                args = [1,]
                CloudProvider.providers[stackId] = DriverClass(*args, **kwargs)
            if stack.type == 'LIBVIRT':
                kwargs['id'] = stack.referenceId
                kwargs['uri'] = stack.apiUrl
                prov = CSLibvirtNodeDriver(**kwargs)
                cb = CloudBrokerConnection(cbip, cbport, cbsecret)
                prov.set_backend(cb)
                CloudProvider.providers[stackId] = prov
        self.cbcl = cbcl
        self.client = CloudProvider.providers[stackId]

    def getSize(self, brokersize, firstdisk):
        providersizes = self.client.list_sizes()
        for s in providersizes:
             if s.ram == brokersize.memory and firstdisk.sizeMax == s.disk:
                return s
        return None

    def getImage(self, imageId):
        iimage = self.cbcl.image.get(imageId)
        for image in self.client.list_images():
            if image.id == iimage.referenceId:
                return image, image


class CloudBroker(object):
    def stackImportImages(self, stackId):
        provider = CloudProvider(stackId)
        if not provider:
            raise RuntimeError('Provider not found')
        count = 0
        stack = provider.cbcl.stack.get(stackId)
        stack.images = []
        for pimage in provider.client.list_images():
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

    def getProviderByStackId(self, stackId):
        return CloudProvider(stackId)
