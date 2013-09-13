#Add extra specific cloudscaler functions for libvirt libcloud driver

from libcloud.compute.drivers.libvirt_driver import LibvirtNodeDriver
from CloudscalerLibcloud.utils import connection
from libcloud.compute.base import NodeImage, NodeSize, Node
from jinja2 import Environment, PackageLoader
import uuid

class CSLibvirtNodeDriver(LibvirtNodeDriver):

    env = Environment(loader=PackageLoader('CloudscalerLibcloud', 'templates'))
    backendconnection = connection.DummyConnection()

    def set_backend(self, connection):
        """
        Set a connection to the cloudbroker backend, this is used
        to get all the supported images and sizes
        """
        self.backendconnection = connection

    def list_sizes(self, location=None):
        """
        Libvirt doesn't has a idea of sizes, because of this we are using
        the cloudscalers internal sizes api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeSize}
        """
        sizes = self.backendconnection.listSizes()
        return [self._to_size(size) for size in sizes]

    def _to_size(self, size):
        return NodeSize(
                id = size['id'],
                name = size['name'],
                ram = size['memory'],
                bandwidth = 0,
                price = 0,
                driver = self,
                disk = size['disk'])



    def list_images(self, location=None):
        """
        Libvirt doesn't has a idea of images, because of this we are using
        the cloudscalers internal images api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeImage}
        """
        images = self.backendconnection.listImages()
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

        return self._to_node(domain)


    def _to_node(self, domain):
         state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
         if state in self.NODE_STATE_MAP:
            state = self.NODE_STATE_MAP[state]
         else:
            state = NodeState.UNKNOWN

         extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(),
                     'types': self.connection.getType(),
                     'used_memory': memory / 1024, 'vcpu_count': vcpu_count,
                     'used_cpu_time': used_cpu_time}
         node = Node(id=domain.ID(), name=domain.name(), state=state,
                        public_ips=[], private_ips=[], driver=self,
                        extra=extra)
         return node
