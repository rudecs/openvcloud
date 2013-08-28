#Add extra specific cloudscaler functions for libvirt libcloud driver

from libcloud.compute.drivers.libvirt_driver import LibvirtNodeDriver
from libcloud.compute.base import NodeImage, NodeSize
from jinja2 import Environment, PackageLoader
import uuid

class CSLibvirtNodeDriver(LibvirtNodeDriver):

    CPUMAPPING = {1: 1700, 2: 3600, 3: 7200}
    env = Environment(loader=PackageLoader('CloudscalerLibcloud', 'templates'))


    def list_sizes(self, location=None):
        """
        Libvirt doesn't has a idea of sizes, because of this we are using
        the cloudscalers internal sizes api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeSize}
        """
        sizes = [{'CU': 2, 'disks': 40, 'guid':
            '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 1, 'name': u'BIG',
            'referenceId': ''},{'CU': 1, 'disks': 20, 'guid':
            '4da91a0d-18f5-47a5-ad97-7cf3b97cbc59', 'id': 2, 'name': u'SMALL',
            'referenceId': ''}]

        return [self._to_size(size) for size in sizes]

    def _to_size(self, size):
        return NodeSize(
                id = size['id'],
                name = size['name'],
                ram = self.CPUMAPPING[size['CU']],
                bandwidth = 0,
                price = 0,
                driver = self,
                disk = size['disks'])



    def list_images(self, location=None):
        """
        Libvirt doesn't has a idea of images, because of this we are using
        the cloudscalers internal images api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeImage}
        """
        images = [{'UNCPath': 'vmhendrik.img',
            'description': '',
            'guid': '3c655a10-7e04-4d93-8ea1-ec5536d9689b',
            'id': 1,
            'name': 'ubuntu-2',
            'referenceId': '',
            'size': 10,
            'type': 'ubuntu'}, {'UNCPath': 'file:///ISOS/windows-2008.iso',
            'description': '',
            'guid': '3c655a10-7e04-4d93-8ea1-ec5536d9689b',
            'id': 2,
            'name': 'windows-2008',
            'referenceId': '',
            'size': 20,
            'type': 'WINDOWS'}]

        return [self._to_image(image) for image in images]

    def _to_image(self, image):
        return NodeImage(
                id = image['id'],
                name = image['name'],
                    driver = self,
                extra = {'path': image['UNCPath'],
                    'size': image['size'],
                    'imagetype': image['type']}
                )

    def create_node(self, name, size, image, location=None, auth=None):
        """
        Creation in libcloud is based on sizes and images, libvirt has no
        knowledge of sizes and images.
        This create_node is specially build to create machines based on extra
        data from the cloudscaler broker.

        @keyword    name:   String with a name for this new node (required)
        @type       name:   C{str}

        @keyword    size:   The size of resources allocated to this node.
                        (required)
        @type       size:   L{NodeSize}

        @keyword    image:  OS Image to boot on node. (required)
        @type       image:  L{NodeImage}

        @keyword    location: Which data center to create a node in. If empty,
                             undefined behavoir will be selected. (optional)
        @type       location: L{NodeLocation}

        @keyword    auth:   Initial authentication information for the node
                           (optional)
        @type       auth:   L{NodeAuthSSHKey} or L{NodeAuthPassword}

        @return: The newly created node.
        @rtype: L{Node}
        """
        storagepool = self.connection.storagePoolLookupByName('VMStor')

        disktemplate = self.env.get_template("disk.xml")
        machinetemplate = self.env.get_template("machine.xml")

        diskname = str(uuid.uuid4())
        diskbasevolume = image.extra['path']
        disksize = size.disk

        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
            diskbasevolume, 'disksize':disksize})

        machinexml = machinetemplate.render({'machinename': name,'diskname':
            diskname, 'memory': size.ram, 'nrcpu': 1})

        #0 means not to preallocate data
        storagepool.createXML(diskxml, 0)
        #0 means default behaviour, e.g machine is auto started.
        domain = self.connection.createXML(machinexml, 0)

        return domain 
