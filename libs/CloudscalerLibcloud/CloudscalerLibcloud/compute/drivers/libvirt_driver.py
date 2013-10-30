# Add extra specific cloudscaler functions for libvirt libcloud driver

from libcloud.compute.drivers.libvirt_driver import LibvirtNodeDriver
from CloudscalerLibcloud.utils import connection
from libcloud.compute.base import NodeImage, NodeSize, Node, NodeState
from jinja2 import Environment, PackageLoader, Template
from xml.etree import ElementTree
import os
import uuid
import libvirt
import urlparse
POOLNAME = 'VMStor'
POOLPATH = '/mnt/%s' % POOLNAME.lower()
libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST = 3


class CSLibvirtNodeDriver(LibvirtNodeDriver):

    def __init__(self, *args, **kwargs):
        super(CSLibvirtNodeDriver, self).__init__(*args, **kwargs)
        self._rndrbn_vnc = 0

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
            id=size['id'],
            name=size['name'],
            ram=size['memory'],
            bandwidth=0,
            price=0,
            driver=self,
            disk=size['disk'])

    def list_images(self, location=None):
        """
        Libvirt doesn't has a idea of images, because of this we are using
        the cloudscalers internal images api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeImage}
        """
        images = self.backendconnection.listImages(self._uri)
        return [self._to_image(image) for image in images]

    def _to_image(self, image): 
        return NodeImage(
            id=image['id'],
            name=image['name'],
            driver=self,
            extra={'path': image['UNCPath'],
                   'size': image['size'],
                   'imagetype': image['type']}
        )

    def _create_disk(self, size, image):
        storagepool = self.connection.storagePoolLookupByName(POOLNAME)
        disktemplate = self.env.get_template("disk.xml")
        diskname = str(uuid.uuid4()) + '.qcow2'
        diskbasevolume = image.extra['path']
        disksize = size.disk
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolume, 'disksize': disksize, 'poolpath': POOLPATH})
        # 0 means not to preallocate data
        storagepool.createXML(diskxml, 0)
        return diskname

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
        diskname = self._create_disk(size, image)
        return self._create_node(name, diskname, size)

    def _create_node(self, name, diskname, size):
        machinetemplate = self.env.get_template("machine.xml")

        macaddress = self.backendconnection.getMacAddress()

        machinexml = machinetemplate.render({'machinename': name, 'diskname': diskname,
                                             'memory': size.ram, 'nrcpu': 1, 'macaddress': macaddress, 'poolpath': POOLPATH})

        # next we set the network configuration.

        network = self.connection.networkLookupByName('default')

        # 0 means default behaviour, e.g machine is auto started.
        domain = self.connection.defineXML(machinexml)
        vmid = domain.UUIDString()
        ipaddress = self.backendconnection.registerMachine(vmid, macaddress)
        extranettemplate = Template("<host mac='{{macaddress}}' name='{{name}}' ip='{{ipaddress}}'/>")
        xmlstring = extranettemplate.render({'macaddress': macaddress, 'name': name, 'ipaddress': ipaddress})
        network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST, libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST, -1, xmlstring, flags=libvirt.VIR_NETWORK_UPDATE_AFFECT_CURRENT)
        domain.create()

        node = self._to_node(domain, ipaddress)
        self._set_persistent_xml(node, domain.XMLDesc(0))
        return node

    def ex_snapshot(self, node, name, snapshottype='internal'):
        domain = self._get_domain_for_node(node=node)
        diskfiles = self._get_domain_disk_file_names(domain)
        snapshot = self.env.get_template('snapshot.xml').render(name=name, diskfiles=diskfiles, type=snapshottype)
        flags = 0 if snapshottype == 'internal' else libvirt.VIR_DOMAIN_SNAPSHOT_CREATE_DISK_ONLY
        return domain.snapshotCreateXML(snapshot, flags).getName()

    def ex_listsnapshots(self, node):
        domain = self._get_domain_for_node(node=node)
        return domain.snapshotListNames(0)

    def ex_snapshot_delete(self, node, name):
        domain = self._get_domain_for_node(node=node)
        snapshot = domain.snapshotLookupByName(name, 0)
        return snapshot.delete(0) == 0

    def ex_snapshot_rollback(self, node, name):
        domain = self._get_domain_for_node(node=node)
        snapshot = domain.snapshotLookupByName(name, 0)
        return domain.revertToSnapshot(snapshot, libvirt.VIR_DOMAIN_SNAPSHOT_REVERT_FORCE) == 0

    def _get_domain_disk_file_names(self, dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        else:
            xml = ElementTree.fromstring(dom.XMLDesc(0))
        disks = xml.findall('devices/disk')
        diskfiles = list()
        for disk in disks:
            if disk.attrib['device'] == 'disk':
                source = disk.find('source')
                if source != None:
                    diskfiles.append(source.attrib['dev'])
        return diskfiles

    def _get_snapshot_disk_file_names(self, snap):
        xml = ElementTree.fromstring(snap.getXMLDesc(0))
        domain = xml.findall('domain')[0]
        return self._get_domain_disk_file_names(domain)

    def destroy_node(self, node):
        domain = self._get_domain_for_node(node=node)

        domid = domain.UUIDString()
        node = self.backendconnection.getNode(domid)
        network = self.connection.networkLookupByName('default')
        extranettemplate = Template("<host mac='{{macaddress}}' ip='{{ipaddress}}'/>")
        xmlstring = extranettemplate.render({'macaddress':node['macaddress'], 'ipaddress':node['ipaddress']})
        try:
            network.update(libvirt.VIR_NETWORK_UPDATE_COMMAND_DELETE, libvirt.VIR_NETWORK_SECTION_IP_DHCP_HOST, -1, xmlstring, flags=libvirt.VIR_NETWORK_UPDATE_AFFECT_CURRENT)
        except libvirt.libvirtError, e:
            # allow operation error incase network is not registered in dhcp
            if e.get_error_code() != libvirt.VIR_ERR_OPERATION_INVALID:
                raise

        self.backendconnection.unregisterMachine(domid)

        diskfiles = self._get_domain_disk_file_names(domain)
        if domain.state(0)[0] != libvirt.VIR_DOMAIN_SHUTOFF:
            domain.destroy()
        for diskfile in diskfiles:
            vol = self.connection.storageVolLookupByPath(diskfile)
            vol.delete(0)
        domain.undefineFlags(libvirt.VIR_DOMAIN_UNDEFINE_SNAPSHOTS_METADATA)
        return True

    def ex_get_console_url(self, node):
        urls = self.backendconnection.listVNC()
        id_ = self._rndrbn_vnc % len(urls)
        url = urls[id_]
        self._rndrbn_vnc += 1
        token = self.backendconnection.storeInfo(self.ex_get_console_info(node), 300)
        return url + "%s" % token

    def list_nodes(self):
        noderesult = []
        nodes = self.backendconnection.listNodes()
        for x in self.connection.listAllDomains(0):
            if x.UUIDString() in nodes:
                ipaddress = nodes[x.UUIDString()]['ipaddress']
            else:
                ipaddress = ''
            noderesult.append(self._to_node(x, ipaddress))
        return noderesult

    def ex_stop(self, node):
        domain = self._get_domain_for_node(node=node)
        return domain.destroy() == 0

    def ex_reboot(self, node):
        domain = self._get_domain_for_node(node=node)
        return domain.reset() == 0

    def ex_start(self, node):
        try:
            domain = self._get_domain_for_node(node=node)
        except libvirt.libvirtError, e:
            if e.get_error_code() == libvirt.VIR_ERR_NO_DOMAIN:
                xml = self._get_persistent_xml(node)
                domain = self.connection.defineXML(xml)
            else:
                raise
        return domain.create() == 0

    def ex_get_console_info(self, node):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain.XMLDesc(0))
        graphics = xml.find('devices/graphics')
        info = dict()
        info['port'] = int(graphics.attrib['port'])
        info['type'] = graphics.attrib['type']
        info['ipaddress'] = self._get_connection_ip()
        return info

    def ex_clone(self, node, size, name):
        snapname = self.ex_snapshot(node, None, 'external')
        origdomain = self._get_domain_for_node(node=node)
        snap = origdomain.snapshotLookupByName(snapname)
        diskname = self._get_snapshot_disk_file_names(snap)[0]
        diskname = os.path.basename(diskname)
        return self._create_node(name, diskname, size)

    def _get_connection_ip(self):
        uri = urlparse.urlparse(self.connection.getURI())
        return uri.netloc

    def _get_persistent_xml(self, node):
        return self.backendconnection.db.get('domain_%s' % node.id)

    def _set_persistent_xml(self, node, xml):
        self.backendconnection.db.set(key='domain_%s' % node.id, value=xml)

    def _remove_persistent_xml(self, node):
        try:
            self.backendconnection.db.delete(key='domain_%s' % node.id)
        except:
            pass

    def _get_domain_for_node(self, node):
        return self.connection.lookupByUUIDString(node.id)

    def _to_node(self, domain, publicipaddress=''):
        state, max_mem, memory, vcpu_count, used_cpu_time = domain.info()
        state = self.NODE_STATE_MAP.get(state, NodeState.UNKNOWN)

        extra = {'uuid': domain.UUIDString(), 'os_type': domain.OSType(),
                 'types': self.connection.getType(),
                 'used_memory': memory / 1024, 'vcpu_count': vcpu_count,
                 'used_cpu_time': used_cpu_time}
        node = Node(id=domain.UUIDString(), name=domain.name(), state=state,
                    public_ips=[publicipaddress], private_ips=[], driver=self,
                    extra=extra)
        return node

