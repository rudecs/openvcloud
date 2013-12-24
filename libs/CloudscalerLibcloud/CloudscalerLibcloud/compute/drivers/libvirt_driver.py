# Add extra specific cloudscaler functions for libvirt libcloud driver

from CloudscalerLibcloud.utils import connection
from libcloud.compute.base import NodeImage, NodeSize, Node, NodeState
from jinja2 import Environment, PackageLoader
from JumpScale.baselib.dnsmasq import DNSMasq
from xml.etree import ElementTree
import uuid
import libvirt
import urlparse
import json
POOLNAME = 'VMStor'
POOLPATH = '/mnt/%s' % POOLNAME.lower()
libvirt.VIR_NETWORK_UPDATE_COMMAND_ADD_LAST = 3


class CSLibvirtNodeDriver():

    NODE_STATE_MAP = {
        0: NodeState.TERMINATED,
        1: NodeState.RUNNING,
        2: NodeState.PENDING,
        3: NodeState.TERMINATED,  # paused
        4: NodeState.TERMINATED,  # shutting down
        5: NodeState.TERMINATED,
        6: NodeState.UNKNOWN,  # crashed
        7: NodeState.UNKNOWN,  # last
    }

    def __init__(self, id, uri):
        self._rndrbn_vnc = 0
        self.id = id
        self.name = id
        self.uri = uri


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
        images = self.backendconnection.listImages(self.id)
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
    def _execute_agent_job(self, name_, id=None, wait=True, **kwargs):
        if not id:
            role = self.id
        return self.backendconnection.agentcontroller_client.executeKwargs('cloudscalers', name_, role, wait=wait, kwargs=kwargs)

    def _create_disk(self, size, image):
        disktemplate = self.env.get_template("disk.xml")
        diskname = str(uuid.uuid4()) + '.qcow2'
        diskbasevolume = image.extra['path']
        disksize = size.disk
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolume, 'disksize': disksize, 'poolpath': POOLPATH})
        self._execute_agent_job('createdisk', diskxml=diskxml, poolname=POOLNAME)
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
        vxlan = self.backendconnection.environmentid

        macaddress = self.backendconnection.getMacAddress()

        machinexml = machinetemplate.render({'machinename': name, 'diskname': diskname, 'vxlan': vxlan,
                                             'memory': size.ram, 'nrcpu': 1, 'macaddress': macaddress, 'poolpath': POOLPATH})


        # 0 means default behaviour, e.g machine is auto started.

        result = self._execute_agent_job('createmachine', machinexml=machinexml)
        vmid = result['id']
        dnsmasq = DNSMasq()
        namespace = 'ns-%s' % vxlan
        dnsmasq.setConfigPath(namespace, self.backendconnection.publicdnsmasqconfigpath)

        ipaddress = self.backendconnection.registerMachine(vmid, macaddress)
        dnsmasq.addHost(macaddress, ipaddress,name)

        node = self._from_agent_to_node(result, ipaddress)
        print result
        self._set_persistent_xml(node, result['XMLDesc'])
        return node

    def ex_snapshot(self, node, name, snapshottype='internal'):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain['XMLDesc'])
        diskfiles = self._get_domain_disk_file_names(xml)
        snapshot = self.env.get_template('snapshot.xml').render(name=name, diskfiles=diskfiles, type=snapshottype)
        return self._execute_agent_job('snapshot', machineid=node.id, snapshottype=snapshottype, xml=snapshot)

    def ex_listsnapshots(self, node):
        return self._execute_agent_job('listsnapshots', machineid=node.id)

    def ex_snapshot_delete(self, node, name):
        return self._execute_agent_job('deletesnapshot', machineid=node.id, name=name)

    def ex_snapshot_rollback(self, node, name):
        return self._execute_agent_job('rollbacksnapshot', machineid=node.id, name=name)

    def _get_domain_disk_file_names(self, dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        elif isinstance(dom, basestring):
            xml = ElementTree.fromstring(dom)
        else:
            raise RuntimeError('Invalid type %s for parameter dom' % type(dom))
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
        backendnode = self.backendconnection.getNode(node.id)
        dnsmasq = DNSMasq()
        namespace = 'ns-%s' % self.backendconnection.environmentid
        dnsmasq.setConfigPath(namespace, self.backendconnection.publicdnsmasqconfigpath)
        dnsmasq.removeHost(backendnode['macaddress'])
        self.backendconnection.unregisterMachine(node.id)
        job = self._execute_agent_job('deletemachine', machineid = node.id)
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
        result = self._execute_agent_job('listmachines')
        for x in result:
            if x['id'] in nodes:
                ipaddress = nodes[x['id']]['ipaddress']
            else:
                ipaddress = ''
            noderesult.append(self._from_agent_to_node(x, ipaddress))
        return noderesult

    def ex_stop(self, node):
        machineid = node.id
        return self._execute_agent_job('stopmachine', machineid = machineid)

    def ex_reboot(self, node):
        machineid = node.id
        return self._execute_agent_job('rebootmachine', machineid = machineid)

    def ex_start(self, node):
        xml = ''
        machineid = node.id 
        return self._execute_agent_job('startmachine', machineid = machineid, xml = xml)
 
    def ex_get_console_info(self, node):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain['XMLDesc'])
        graphics = xml.find('devices/graphics')
        info = dict()
        info['port'] = int(graphics.attrib['port'])
        info['type'] = graphics.attrib['type']
        info['ipaddress'] = self._get_connection_ip()
        return info

    #def ex_clone(self, node, size, name):
    #    snapname = self.ex_snapshot(node, None, 'external')
    #    origdomain = self._get_domain_for_node(node=node)
    #    snap = origdomain.snapshotLookupByName(snapname)
    #    diskname = self._get_snapshot_disk_file_names(snap)[0]
    #    diskname = os.path.basename(diskname)
    #    return self._create_node(name, diskname, size)

    def _get_connection_ip(self):
        uri = urlparse.urlparse(self.uri)
        return uri.netloc

    def _get_persistent_xml(self, node):
        return self.backendconnection.db.get('domain_%s' % node.id)


    def _set_persistent_xml(self, node, xml):
        self.backendconnection.db.set(key='domain_%s' % node.id, obj=xml)

    def _remove_persistent_xml(self, node):
        try:
            self.backendconnection.db.delete(key='domain_%s' % node.id)
        except:
            pass

    def _get_domain_for_node(self, node):
        return self._execute_agent_job('getmachine', machineid = node.id)

    def _from_agent_to_node(self, domain, publicipaddress=''):
        state = self.NODE_STATE_MAP.get(domain['state'], NodeState.UNKNOWN)
        extra = domain['extra']
        node = Node(id=domain['id'], name=domain['name'], state=domain['state'],
                    public_ips=[publicipaddress], private_ips=[], driver=self,
                    extra=extra)
        return node


