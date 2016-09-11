# Add extra specific cloudscaler functions for libvirt libcloud driver
from JumpScale import j
from CloudscalerLibcloud.utils import connection
from libcloud.compute.base import NodeImage, NodeSize, Node, NodeState, StorageVolume
from jinja2 import Environment, PackageLoader
from xml.etree import ElementTree
import urlparse
import json
import uuid
import crypt
import random
import string
import time

baselength = len(string.lowercase)
env = Environment(loader=PackageLoader('CloudscalerLibcloud', 'templates'))


def convertnumber(number):
    output = ''
    if number == 0:
        return string.lowercase[0]
    segment = number // baselength
    remainder = number % baselength
    if segment > 0:
        output += convertnumber(segment - 1)
    output += string.lowercase[remainder]

    return output


def convertchar(word):
    number = 0
    word = list(reversed(word))
    for idx in xrange(len(word) - 1, -1, -1):
        addme = 1 if idx != 0 else 0
        number += (addme + string.lowercase.index(word[idx])) * baselength ** idx
    return number


class NetworkInterface(object):
    def __init__(self, mac, target, type):
        self.mac = mac
        self.target = target
        self.type = type


class OpenvStorageVolume(StorageVolume):
    def __init__(self, *args, **kwargs):
        super(OpenvStorageVolume, self).__init__(*args, **kwargs)
        url = urlparse.urlparse(self.id)
        self.edgetransport = 'tcp' if '+' not in url.scheme else url.scheme.split('+')[1]
        self.edgehost = url.hostname
        self.edgeport = url.port
        self.name = url.path.strip('/')
        self.type = 'disk'
        self.bus = 'virtio'

    def __str__(self):
        template = env.get_template("ovsdisk.xml")
        return template.render(self.__dict__)


class OpenvStorageISO(OpenvStorageVolume):
    def __init__(self, *args, **kwargs):
        super(OpenvStorageISO, self).__init__(*args, **kwargs)
        self.dev = 'hdc'
        self.type = 'cdrom'
        self.bus = 'ide'


def OpenvStorageVolumeFromXML(disk, driver):
    source = disk.find('source')
    protocol = source.attrib.get('protocol')
    name = source.attrib.get('name')
    host = source.find('host')
    hostname = host.attrib.get('name')
    hostport = host.attrib.get('port')
    transport = host.attrib.get('transport', 'tcp')
    url = "{protocol}+{transport}://{hostname}:{port}/{name}".format(
        protocol=protocol,
        transport=transport,
        hostname=hostname,
        port=hostport,
        name=name
    )
    return OpenvStorageVolume(id=url, name='N/A', size=0, driver=driver)


class CSLibvirtNodeDriver(object):

    _roundrobinstoragedriver = {'next': 0, 'edgeclienttime': 0}
    _edgeclients = []
    _edgenodes = {}

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

    def __init__(self, id, gid, uri):
        self._rndrbn_vnc = 0
        self.id = id
        self.gid = gid
        self.name = 'libvirt'
        self.uri = uri
        self.env = env
        self.scl = j.clients.osis.getNamespace('system')

    backendconnection = connection.DummyConnection()

    @property
    def edgeclients(self):
        if self._roundrobinstoragedriver['edgeclienttime'] < time.time() - 60:
            edgeclients = self._execute_agent_job('listedgeclients', role='storagedriver')
            vpools = set(client['vpool'] for client in edgeclients)
            if len(vpools) > 1:
                vpools.remove('vmstor')

            activesessions = self.backendconnection.agentcontroller_client.listActiveSessions()

            def filter_clients(client):
                node = self._edgenodes.get(client['ip'])
                if node is None:
                    node = next(iter(self.scl.node.search({'gid': self.gid, 'netaddr.ip': client['ip']})[1:]), None)
                    if node is None:
                        return False
                client['nid'] = node['id']
                if (node['gid'], node['id']) not in activesessions:
                    return False
                if client['vpool'] not in vpools:
                    return False
                return True

            self._edgeclients[:] = filter(filter_clients, edgeclients)
            self._roundrobinstoragedriver['edgeclienttime'] = time.time()
        return self._edgeclients

    def getNextEdgeClient(self):
        self._roundrobinstoragedriver['next'] += 1
        rndrbn = self._roundrobinstoragedriver['next']
        clients = self.edgeclients
        return clients[rndrbn % len(clients)]

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
            extra={'vcpus': size['vcpus']},
            driver=self,
            disk=size['disk'])

    def ex_list_images(self, location=None):
        """
        Libvirt doesn't has a idea of images, because of this we are using
        the cloudscalers internal images api.
        At this moment location is always None and can be neglected
        @param location: Optional location, not used at the moment
        @type: C{str}
        @rtype: C{list} of L{NodeImage}
        """
        providerid = "%s_%s" % (self.gid, self.id)
        images = self.backendconnection.listImages(providerid)
        return [self._to_image(image) for image in images]

    def _to_image(self, image):
        username = None
        if image.get('extra'):
            extra = json.loads(image['extra'])
            if 'username' in extra:
                username = extra['username']
        return NodeImage(
            id=image['id'],
            name=image['name'],
            driver=self,
            extra={'path': image['UNCPath'],
                   'size': image['size'],
                   'imagetype': image['type'],
                   'username': username}
        )

    def _execute_agent_job(self, name_, id=None, wait=True, queue=None, role=None, **kwargs):
        if not id and not role:
            id = int(self.id)
        else:
            id = id and int(id)
        job = self.backendconnection.agentcontroller_client.executeJumpscript('cloudscalers', name_, nid=id, role=role, gid=self.gid, wait=wait, queue=queue, args=kwargs)
        if wait and job['state'] != 'OK':
            if job['state'] == 'NOWORK':
                raise RuntimeError('Could not find agent with nid:%s' % id)
            elif job['state'] == 'TIMEOUT':
                raise RuntimeError('Job failed to execute on time')
            else:
                raise RuntimeError("Could not execute %s for nid:%s, error was:%s" % (name_, id, job['result']))
        if wait:
            return job['result']
        else:
            return job

    def _create_disk(self, vm_id, size, image, disk_role='base'):
        templateguid = str(uuid.UUID(image.id))
        disksize = size.disk * (1000 ** 3)  # from GB to bytes
        return self._execute_agent_job('createdisk', vmname=vm_id, size=disksize, role='storagedriver', templateguid=templateguid)

    def create_volume(self, size, name):
        bytesize = size * (1000 ** 3)
        volumes = [{'name': name, 'size': bytesize, 'dev': ''}]
        return self.create_volumes(volumes)[0]

    def create_volumes(self, volumes):
        stvolumes = []
        for volume in volumes:
            edgeclient = self.getNextEdgeClient()
            volume = self._execute_agent_job('createvolume', volume=volume, id=edgeclient['nid'], edgeclient=edgeclient)
            stvol = OpenvStorageVolume(id=volume['id'], size=volume['size'], name=volume['name'], driver=self)
            stvol.dev = volume['dev']
            stvolumes.append(stvol)
        return stvolumes

    def attach_volume(self, node, volume):
        def getNextDev(devices):
            devid = 0

            for target in devices.iterfind('disk/target'):
                if target.attrib['bus'] != 'virtio':
                    continue
                dev = convertchar(target.attrib.get('dev', 'vda')[2:])
                if dev > devid:
                    devid = dev
            return 'vd%s' % convertnumber(devid + 1)

        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        devices = dom.find('devices')
        dev = getNextDev(devices)
        volume.dev = dev
        self._execute_agent_job('attach_device', queue='hypervisor', xml=str(volume), machineid=node.id)
        devices.append(ElementTree.fromstring(str(volume)))
        domxml = ElementTree.tostring(dom)
        return self._update_node(node, domxml)

    def _update_node(self, node, xml):
        self._set_persistent_xml(node, xml)
        return self._from_xml_to_node(xml, node)

    def destroy_volume(self, volume):
        return self._execute_agent_job('destroyvolume', role='storagedriver', path=volume.id)

    def detach_volume(self, volume):
        node = volume.extra['node']
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        devices = dom.find('devices')
        domxml = None

        for disk in devices.iterfind('disk'):
            if disk.attrib['device'] != 'disk':
                continue
            source = disk.find('source')
            if source.attrib.get('dev', source.attrib.get('name')) == volume.name:
                diskxml = ElementTree.tostring(disk)
                self._execute_agent_job('detach_device', queue='hypervisor', xml=diskxml, machineid=node.id)
                devices.remove(disk)
                domxml = ElementTree.tostring(dom)
        if domxml:
            return self._update_node(node, domxml)
        return node

    def _create_clone_disk(self, vm_id, size, clone_disk, disk_role='base'):
        disktemplate = self.env.get_template("disk.xml")
        diskname = vm_id + '-' + disk_role + '.raw'
        diskbasevolume = clone_disk
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolume, 'disksize': size.disk})
        poolname = vm_id
        self._execute_agent_job('createdisk', diskxml=diskxml, role='storagedriver', poolname=poolname)
        return diskname

    def _create_metadata_iso(self, name, userdata, metadata, type):
        return self._execute_agent_job('createmetaiso', role='storagedriver', name=name, metadata=metadata, userdata=userdata, type=type)

    def generate_password_hash(self, password):
        def generate_salt():
            salt_set = ('abcdefghijklmnopqrstuvwxyz'
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        '0123456789./')
            salt = 16 * ' '
            return ''.join([random.choice(salt_set) for c in salt])
        salt = generate_salt()
        return crypt.crypt(password, '$6$' + salt)

    def create_node(self, name, size, image, location=None, auth=None, networkid=None, datadisks=None):
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
        metadata_iso = None

        if auth:
            # At this moment we handle only NodeAuthPassword
            password = auth.password
            if image.extra['imagetype'] not in ['WINDOWS', 'Windows']:
                userdata = {'password': password,
                            'users': [{'name': 'cloudscalers',
                                       'plain_text_passwd': password,
                                       'lock-passwd': False,
                                       'shell': '/bin/bash',
                                       'sudo': 'ALL=(ALL) ALL'}],
                            'ssh_pwauth': True,
                            'manage_etc_hosts': True,
                            'chpasswd': {'expire': False}}
                metadata = {'local-hostname': name}
            else:
                userdata = {}
                metadata = {'admin_pass': password, 'hostname': name}
            metadata_iso = self._create_metadata_iso(name, userdata, metadata, image.extra['imagetype'])
        diskpath = self._create_disk(name, size, image)
        if not diskpath or diskpath == -1:
            # not enough free capcity to create a disk on this node
            return -1
        volume = OpenvStorageVolume(id=diskpath, name='Bootdisk', size=size, driver=self)
        volume.dev = 'vda'
        volumes = [volume]
        if datadisks:
            datavolumes = []
            for idx, (diskname, disksize) in enumerate(datadisks):
                volume = {'name': diskname, 'size': disksize * (1000 ** 3), 'dev': 'vd%s' % convertnumber(idx + 1)}
                datavolumes.append(volume)
            volumes += self.create_volumes(datavolumes)
        return self._create_node(name, size, metadata_iso, networkid, volumes)

    def _create_node(self, name, size, metadata_iso=None, networkid=None, volumes=None):
        volumes = volumes or []
        machinetemplate = self.env.get_template("machine.xml")
        vxlan = '%04x' % networkid
        macaddress = self.backendconnection.getMacAddress(self.gid)

        result = self._execute_agent_job('createnetwork', queue='hypervisor', networkid=networkid)
        if not result or result == -1:
            return -1

        networkname = result['networkname']
        if metadata_iso:
            metadata_iso = str(OpenvStorageISO(id=metadata_iso, size=0, name='N/A', driver=self))
        machinexml = machinetemplate.render({'machinename': name, 'isoname': metadata_iso, 'vxlan': vxlan,
                                             'memory': size.ram, 'nrcpu': size.extra['vcpus'], 'macaddress': macaddress,
                                             'network': networkname, 'volumes': volumes})

        # 0 means default behaviour, e.g machine is auto started.
        result = self._execute_agent_job('createmachine', queue='hypervisor', machinexml=machinexml)
        if not result or result == -1:
            # Agent is not registered to agentcontroller or we can't provision the machine(e.g not enough resources, delete machine)
            if result == -1:
                self._execute_agent_job('deletemachine', queue='hypervisor', machineid=None, machinexml=machinexml)
            return -1

        vmid = result['id']
        self.backendconnection.registerMachine(vmid, macaddress, networkid)
        node = self._from_agent_to_node(result, volumes=volumes)
        self._set_persistent_xml(node, machinexml)
        return node

    def ex_create_template(self, node, name, imageid, snapshotbase=None):
        xml = self._get_persistent_xml(node)
        node = self._from_xml_to_node(xml, None)
        bootvolume = node.extra['volumes'][0]
        return self._execute_agent_job('createtemplate', wait=False, queue='io',
                                       machineid=node.id, templatename=name,
                                       sourcepath=bootvolume.id,
                                       imageid=imageid)

    def ex_get_node_details(self, node_id):
        node = Node(id=node_id, name='', state='', public_ips=[], private_ips=[], driver='')  # dummy Node as all we want is the ID
        agentnode = self._get_domain_for_node(node)
        if agentnode is None:
            xml = self._get_persistent_xml(node)
            agentnode = {'id': node_id, 'name': '', 'state': 5, 'extra': {}, 'XMLDesc': xml}
        node = self._from_agent_to_node(agentnode)
        return node

    def _get_volume_paths(self, node):
        diskpaths = list()
        for volume in node.extra['volumes']:
            diskpaths.append(volume.id)
        return diskpaths

    def ex_create_snapshot(self, node, name):
        diskpaths = self._get_volume_paths(node)
        return self._execute_agent_job('snapshot', role='storagedriver', diskpaths=diskpaths, name=name)

    def ex_list_snapshots(self, node):
        diskpaths = self._get_volume_paths(node)
        return self._execute_agent_job('listsnapshots', role='storagedriver', diskpaths=diskpaths)

    def ex_delete_snapshot(self, node, timestamp):
        diskpaths = self._get_volume_paths(node)
        return self._execute_agent_job('deletesnapshot', wait=False, role='storagedriver', diskpaths=diskpaths, timestamp=timestamp)

    def ex_rollback_snapshot(self, node, timestamp):
        diskpaths = self._get_volume_paths(node)
        return self._execute_agent_job('rollbacksnapshot', role='storagedriver', diskpaths=diskpaths, timestamp=timestamp)

    def _get_domain_disk_file_names(self, dom, disktype='disk'):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        elif isinstance(dom, basestring):
            xml = ElementTree.fromstring(dom)
        else:
            raise RuntimeError('Invalid type %s for parameter dom' % type(dom))
        disks = xml.findall('devices/disk')
        diskfiles = list()
        for disk in disks:
            if disktype is None or disk.attrib['device'] == disktype:
                source = disk.find('source')
                if source is not None:
                    if source.attrib.get('protocol') == 'openvstorage':
                        ovsdisk = OpenvStorageVolumeFromXML(disk, self)
                        diskfiles.append(ovsdisk.id)
                    elif 'dev' in source.attrib:
                        diskfiles.append(source.attrib['dev'])
                    elif 'file' in source.attrib:
                        diskfiles.append(source.attrib['file'])
        return diskfiles

    def _get_snapshot_disk_file_names(self, xml):
        xml = ElementTree.fromstring(xml)
        domain = xml.findall('domain')[0]
        return self._get_domain_disk_file_names(domain)

    def destroy_node(self, node):
        xml = self._get_persistent_xml(node)
        self.backendconnection.unregisterMachine(node.id)
        self._execute_agent_job('deletemachine', queue='hypervisor', machineid=node.id, machinexml=xml)
        files = self._get_domain_disk_file_names(xml, None)
        self._execute_agent_job('destroyvolumes', diskpaths=files, role='storagedriver')
        return True

    def ex_get_console_url(self, node):
        urls = self.backendconnection.listVNC(self.gid)
        id_ = self._rndrbn_vnc % len(urls)
        url = urls[id_]
        self._rndrbn_vnc += 1
        token = self.backendconnection.storeInfo(self.ex_get_console_output(node), 300)
        return url + "%s" % token

    def list_nodes(self):
        noderesult = []
        nodes = self.backendconnection.listNodes()
        result = self._execute_agent_job('listmachines', queue='default')
        for x in result:
            if x['id'] in nodes:
                ipaddress = nodes[x['id']]['ipaddress']
            else:
                ipaddress = ''
            noderesult.append(self._from_agent_to_node(x, ipaddress))
        return noderesult

    def ex_stop_node(self, node):
        machineid = node.id
        return self._execute_agent_job('stopmachine', queue='hypervisor', machineid=machineid)

    def ex_suspend_node(self, node):
        machineid = node.id
        return self._execute_agent_job('suspendmachine', queue='hypervisor', machineid=machineid)

    def ex_resume_node(self, node):
        machineid = node.id
        return self._execute_agent_job('resumemachine', queue='hypervisor', machineid=machineid)

    def ex_pause_node(self, node):
        machineid = node.id
        return self._execute_agent_job('pausemachine', queue='hypervisor', machineid=machineid)

    def ex_unpause_node(self, node):
        machineid = node.id
        return self._execute_agent_job('unpausemachine', queue='hypervisor', machineid=machineid)

    def ex_soft_reboot_node(self, node):
        if self._ensure_network(node) == -1:
            return -1
        xml = self._get_persistent_xml(node)
        return self._execute_agent_job('softrebootmachine', queue='hypervisor', machineid=node.id, xml=xml)

    def ex_hard_reboot_node(self, node):
        if self._ensure_network(node) == -1:
            return -1
        xml = self._get_persistent_xml(node)
        return self._execute_agent_job('hardrebootmachine', queue='hypervisor', machineid=node.id, xml=xml)

    def _ensure_network(self, node):
        backendnode = self.backendconnection.getNode(node.id)
        networkid = backendnode['networkid']
        result = self._execute_agent_job('createnetwork', queue='hypervisor', networkid=networkid)
        if not result or result == -1:
            return -1
        return True

    def ex_start_node(self, node):
        xml = self._get_persistent_xml(node)
        if self._ensure_network(node) == -1:
            return -1
        self._execute_agent_job('startmachine', queue='hypervisor', machineid=node.id, xml=xml)
        return True

    def ex_get_console_output(self, node):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain['XMLDesc'])
        graphics = xml.find('devices/graphics')
        info = dict()
        info['port'] = int(graphics.attrib['port'])
        info['type'] = graphics.attrib['type']
        info['ipaddress'] = self._get_connection_ip()
        return info

    def ex_clone(self, node, size, vmid, networkid, diskmapping):
        name = 'vm-%s' % vmid
        diskpaths = self._execute_agent_job('clonevolumes', name=name, machineid=node.id, role='storagedriver', diskmapping=diskmapping)
        volumes = []
        for idx, path in enumerate(diskpaths):
            volume = OpenvStorageVolume(id=path, name='N/A', size=-1, driver=self)
            volume.dev = 'vd%s' % convertnumber(idx)
            volumes.append(volume)
        return self. _create_node(name, size, networkid=networkid, volumes=volumes)

    def ex_export(self, node, exportname, uncpath, emailaddress):
        machineid = node.id
        return self._execute_agent_job('backupmachine', wait=False, machineid=machineid, backupname=exportname, location=uncpath, emailaddress=emailaddress)

    def ex_is_storage_action_running(self, node):
        """
        Check if an action is being running that is doing some interactions
        with the disk
        """
        machineid = node.id
        return self._execute_agent_job('checkstorageaction', wait=True, machineid=machineid)

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
        return self._execute_agent_job('getmachine', queue='hypervisor', machineid=node.id)

    def _from_agent_to_node(self, domain, publicipaddress='', volumes=None):
        xml = domain.get('XMLDesc')
        node = Node(id=domain['id'],
                    public_ips=[],
                    name=domain['name'],
                    private_ips=[],
                    state=domain['state'],
                    driver=self)
        if xml:
            node = self._from_xml_to_node(xml, node)
        node.state = domain['state']
        extra = domain['extra']
        node.extra.update(extra)
        if volumes:
            node.extra['volumes'] = volumes
        if publicipaddress:
            node.public_ips.append(publicipaddress)
        return node

    def _from_xml_to_node(self, xml, node=None):
        dom = ElementTree.fromstring(xml)
        state = NodeState.UNKNOWN
        volumes = list()
        ifaces = list()
        for disk in dom.findall('devices/disk'):
            if disk.attrib['device'] != 'disk':
                continue
            volume = OpenvStorageVolumeFromXML(disk, self)
            volumes.append(volume)
        for nic in dom.findall('devices/interface'):
            mac = None
            macelement = nic.find('mac')
            if macelement is not None:
                mac = macelement.attrib['address']
            target = nic.find('target').attrib['dev']
            type = nic.attrib['type']
            ifaces.append(NetworkInterface(mac=mac, target=target, type=type))
        name = dom.find('name').text
        extra = {'volumes': volumes, 'ifaces': ifaces}
        if node is None:
            id = dom.find('uuid').text
            node = Node(id=id, name=name, state=state,
                        public_ips=[], private_ips=[], driver=self,
                        extra=extra)
        else:
            node.extra.update(extra)
        return node

    def ex_snapshots_can_be_deleted_while_running(self):
        """
        FOR LIBVIRT A SNAPSHOT CAN'T BE DELETED WHILE MACHINE RUNNGIN
        """
        return False

    def attach_public_network(self, node):
        """
        Attach Virtual machine to the cpu node public network
        """
        macaddress = self.backendconnection.getMacAddress(self.gid)
        iface = ElementTree.Element('interface')
        iface.attrib['type'] = 'network'
        target = '%s-pub' % node.name
        ElementTree.SubElement(iface, 'source').attrib = {'network': 'public'}
        ElementTree.SubElement(iface, 'mac').attrib = {'address': macaddress}
        ElementTree.SubElement(iface, 'model').attrib = {'type': 'virtio'}
        ElementTree.SubElement(iface, 'target').attrib = {'dev': target}
        ifacexml = ElementTree.tostring(iface)
        self._execute_agent_job('attach_device', queue='hypervisor', xml=ifacexml, machineid=node.id)
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        devices = dom.find('devices')
        devices.append(iface)
        domxml = ElementTree.tostring(dom)
        self._update_node(node, domxml)
        return NetworkInterface(mac=macaddress, target=target, type='bridge')

    def detach_public_network(self, node, networkid):
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        devices = dom.find('devices')
        interfacexml = None
        targetname = '%s-pub' % node.name
        for interface in devices.iterfind('interface'):
            target = interface.find('target')
            if target.attrib['dev'] == targetname:
                devices.remove(interface)
                interfacexml = ElementTree.tostring(interface)
                break
        if interfacexml:
            domxml = self._execute_agent_job('detach_device', queue='hypervisor', xml=interfacexml, machineid=node.id)
            domxml = ElementTree.tostring(dom)
            return self._update_node(node, domxml)

    def ex_resize(self, node, size):
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        memory = dom.find('memory')
        if dom.find('currentMemory') is not None:
            dom.remove(dom.find('currentMemory'))
        memory.text = str(size.ram * 1024)
        vcpu = dom.find('vcpu')
        vcpu.text = str(size.extra['vcpus'])
        xml = ElementTree.tostring(dom)
        self._set_persistent_xml(node, xml)
        return True

    def ex_migrate(self, node, sourceprovider, force=False):
        domainxml = self._get_persistent_xml(node)
        self._execute_agent_job('vm_livemigrate',
                                vm_id=node.id,
                                sourceurl=sourceprovider.uri,
                                force=force,
                                domainxml=domainxml)
        return True
