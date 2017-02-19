# Add extra specific cloudscaler functions for libvirt libcloud driver
from JumpScale import j
from CloudscalerLibcloud.utils import connection
from libcloud.compute.base import NodeImage, NodeSize, Node, NodeState, StorageVolume
from libcloud.compute.drivers.dummy import DummyNodeDriver
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


class LibvirtState:
    RUNNING = 1
    HALTED = 5


class StorageException(Exception):

    def __init__(self, msg, e):
        super(StorageException, self).__init__(msg)
        self.origexception = e

    def __str__(self):
        return "{}, {}".format(self.message, self.origexception)


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
        self.iops = kwargs.pop('iops', 0)
        super(OpenvStorageVolume, self).__init__(*args, **kwargs)
        vdiskid, _, vdiskguid = self.id.partition('@')
        url = urlparse.urlparse(vdiskid)
        self.vdiskguid = vdiskguid
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
    vdiskguid = source.attrib.get('vdiskguid')
    hostname = host.attrib.get('name')
    hostport = host.attrib.get('port')
    transport = host.attrib.get('transport', 'tcp')
    url = "{protocol}+{transport}://{hostname}:{port}/{name}@{vdiskguid}".format(
        protocol=protocol,
        transport=transport,
        hostname=hostname,
        port=hostport,
        name=name,
        vdiskguid=vdiskguid
    )
    return OpenvStorageVolume(id=url, name='N/A', size=0, driver=driver)


class CSLibvirtNodeDriver(object):

    _ovsdata = {}
    _edgenodes = {}
    type = 'CSLibvirt'

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
    def ovs_credentials(self):
        cachekey = 'credentials_{}'.format(self.gid)
        if cachekey not in self._ovsdata:
            grid = self.scl.grid.get(self.gid)
            credentials = grid.settings['ovs_credentials']
            self._ovsdata[cachekey] = credentials
        return self._ovsdata[cachekey]

    @property
    def ovs_connection(self):
        cachekey = 'ovs_connection_{}'.format(self.gid)
        if cachekey not in self._ovsdata:
            connection = {'ips': self.ovs_credentials['ips'],
                          'client_id': self.ovs_credentials['client_id'],
                          'client_secret': self.ovs_credentials['client_secret']}
            self._ovsdata[cachekey] = connection
        return self._ovsdata[cachekey]

    @property
    def ovs_settings(self):
        cachekey = 'ovs_settings_{}'.format(self.gid)
        if cachekey not in self._ovsdata:
            grid = self.scl.grid.get(self.gid)
            grid_settings = grid.settings.get('ovs_settings', dict())
            settings = dict(vpool_vmstor_metadatacache=grid_settings.get('vpool_vmstor_metadatacache', 20),
                            vpool_data_metadatacache=grid_settings.get('vpool_data_metadatacache', 20))
            self._ovsdata[cachekey] = settings
        return self._ovsdata[cachekey]

    def getVolumeId(self, vdiskguid, edgeclient, name):
        return "openvstorage+{protocol}://{ip}:{port}/{name}@{vdiskguid}".format(
            protocol=edgeclient.get('protocol', 'tcp'),
            ip=edgeclient['storageip'],
            port=edgeclient['edgeport'],
            name=name,
            vdiskguid=vdiskguid
        )

    @property
    def edgeclients(self):
        edgeclients = self._execute_agent_job('listedgeclients', role='storagemaster',
                                              ovs_connection=self.ovs_connection)

        activesessions = self.backendconnection.agentcontroller_client.listActiveSessions()

        def filter_clients(client):
            node = self._edgenodes.get(client['storageip'])
            if node is None:
                node = next(iter(self.scl.node.search({'gid': self.gid, 'netaddr.ip': client['storageip']})[1:]), None)
                if node is None:
                    return False
                else:
                    self._edgenodes[client['storageip']] = node
            client['nid'] = node['id']
            if (node['gid'], node['id']) not in activesessions:
                return False
            return True

        return filter(filter_clients, edgeclients)

    def getNextEdgeClient(self, vpool, edgeclients=None):
        clients = edgeclients or self.edgeclients[:]
        clients = filter(lambda x: x['vpool'] == vpool, clients)
        return sorted(clients, key=lambda client: client['vdiskcount'])[0]

    def getEdgeClientFromVolume(self, volume):
        edgeclients = self.edgeclients[:]
        for edgeclient in edgeclients:
            if volume.edgehost == edgeclient['storageip'] and volume.edgeport == edgeclient['edgeport']:
                return edgeclient, edgeclients

    def getBestDataVpool(self):
        edgeclients = self.edgeclients[:]
        diskspervpool = {}
        for edgeclient in edgeclients:
            diskspervpool[edgeclient['vpool']] = diskspervpool.setdefault(
                edgeclient['vpool'], 0) + edgeclient['vdiskcount']
        if len(diskspervpool) > 1:
            diskspervpool.pop('vmstor', None)
        # get vpool with least vdiskcount
        return sorted(diskspervpool.items(), key=lambda vpool: vpool[1])[0][0], edgeclients

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

        elif id is None:
            id = 0
        else:
            id = id and int(id)
        job = self.backendconnection.agentcontroller_client.executeJumpscript(
            'greenitglobe', name_, nid=id, role=role, gid=self.gid, wait=wait, queue=queue, args=kwargs)
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
        edgeclient = self.getNextEdgeClient('vmstor')
        diskname = '{0}/bootdisk-{0}'.format(vm_id)
        kwargs = {'ovs_connection': self.ovs_connection,
                  'storagerouterguid': edgeclient['storagerouterguid'],
                  'size': size.disk,
                  'templateguid': templateguid,
                  'diskname': diskname,
                  'pagecache_ratio': self.ovs_settings['vpool_vmstor_metadatacache']}
        vdiskguid = self._execute_agent_job('creatediskfromtemplate', role='storagedriver', **kwargs)
        volumeid = self.getVolumeId(vdiskguid=vdiskguid, edgeclient=edgeclient, name=diskname)
        return OpenvStorageVolume(id=volumeid, name='Bootdisk', size=size, driver=self)

    def create_volume(self, size, name):
        volumes = [{'name': name, 'size': size, 'dev': ''}]
        return self.create_volumes(volumes)[0]

    def create_volumes(self, volumes):
        stvolumes = []
        for volume in volumes:
            vpoolname, edgeclients = self.getBestDataVpool()
            edgeclient = self.getNextEdgeClient(vpoolname, edgeclients)
            diskname = 'volumes/volume_{}'.format(volume['name'])
            kwargs = {'ovs_connection': self.ovs_connection,
                      'vpoolguid': edgeclient['vpoolguid'],
                      'storagerouterguid': edgeclient['storagerouterguid'],
                      'diskname': diskname,
                      'size': volume['size'],
                      'pagecache_ratio': self.ovs_settings['vpool_data_metadatacache']}
            vdiskguid = self._execute_agent_job('createdisk', role='storagedriver', **kwargs)
            volumeid = self.getVolumeId(vdiskguid=vdiskguid, edgeclient=edgeclient, name=diskname)
            stvol = OpenvStorageVolume(id=volumeid, size=volume['size'], name=diskname, driver=self)
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
        return self.destroy_volumes_by_guid([volume.vdiskguid])

    def get_volume_from_xml(self, xmldom, volume):
        devices = xmldom.find('devices')
        for disk in devices.iterfind('disk'):
            if disk.attrib['device'] != 'disk':
                continue
            source = disk.find('source')
            if source.attrib.get('dev', source.attrib.get('name')) == volume.name:
                return devices, disk
        return None, None

    def detach_volume(self, volume):
        node = volume.extra['node']
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        domxml = None
        devices, disk = self.get_volume_from_xml(dom, volume)
        if disk is not None:
            diskxml = ElementTree.tostring(disk)
            self._execute_agent_job('detach_device', queue='hypervisor', xml=diskxml, machineid=node.id)
            devices.remove(disk)
            domxml = ElementTree.tostring(dom)
        if domxml:
            return self._update_node(node, domxml)
        return node

    def _create_metadata_iso(self, name, userdata, metadata, type):
        volumeid = self._execute_agent_job('createmetaiso', role='storagedriver',
                                           name=name, metadata=metadata, userdata=userdata, type=type)
        return OpenvStorageISO(id=volumeid, size=0, name='N/A', driver=self)

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
        volumes = []

        try:
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
                volumes.append(self._create_metadata_iso(name, userdata, metadata, image.extra['imagetype']))

            volume = self._create_disk(name, size, image)
            volume.dev = 'vda'
            volumes.append(volume)
            if datadisks:
                datavolumes = []
                for idx, (diskname, disksize) in enumerate(datadisks):
                    volume = {'name': diskname, 'size': disksize, 'dev': 'vd%s' % convertnumber(idx + 1)}
                    datavolumes.append(volume)
                volumes += self.create_volumes(datavolumes)
        except Exception as e:
            if len(volumes) > 0:
                self.destroy_volumes_by_guid([volume.vdiskguid for volume in volumes])
            raise StorageException('Failed to create some volumes', e)
        try:
            return self._create_node(name, size, networkid, volumes)
        except:
            if len(volumes) > 0:
                self.destroy_volumes_by_guid([volume.vdiskguid for volume in volumes])
            raise

    def _create_node(self, name, size, networkid=None, volumes=None):
        volumes = volumes or []
        machinetemplate = self.env.get_template("machine.xml")
        vxlan = '%04x' % networkid
        macaddress = self.backendconnection.getMacAddress(self.gid)

        result = self._execute_agent_job('createnetwork', queue='hypervisor', networkid=networkid)
        if not result or result == -1:
            return -1

        networkname = result['networkname']
        machinexml = machinetemplate.render({'machinename': name, 'vxlan': vxlan,
                                             'memory': size.ram, 'nrcpu': size.extra['vcpus'], 'macaddress': macaddress,
                                             'network': networkname, 'volumes': volumes})

        # 0 means default behaviour, e.g machine is auto started.
        result = self._execute_agent_job('createmachine', queue='hypervisor', machinexml=machinexml)
        if not result or result == -1:
            # Agent is not registered to agentcontroller or we can't provision the
            # machine(e.g not enough resources, delete machine)
            if result == -1:
                self._execute_agent_job('deletemachine', queue='hypervisor', machineid=None, machinexml=machinexml)
            return -1

        vmid = result['id']
        self.backendconnection.registerMachine(vmid, macaddress, networkid)
        node = self._from_agent_to_node(result, volumes=volumes)
        self._set_persistent_xml(node, machinexml)
        return node

    def ex_create_template(self, node, name):
        xml = self._get_persistent_xml(node)
        node = self._from_xml_to_node(xml, node)
        bootvolume = node.extra['volumes'][0]
        kwargs = {'ovs_connection': self.ovs_connection,
                  'diskguid': bootvolume.vdiskguid}
        templateguid = self._execute_agent_job('createtemplate', queue='io', role='storagedriver', **kwargs)
        return self.backendconnection.registerImage(name, 'Custom Template', templateguid, 0, self.gid)

    def ex_delete_template(self, templateid):
        kwargs = {'ovs_connection': self.ovs_connection, 'diskguid': str(uuid.UUID(templateid))}
        self._execute_agent_job('deletetemplate', queue='io', role='storagedriver', **kwargs)
        return self.backendconnection.removeImage(templateid, self.gid)

    def ex_get_node_details(self, node_id):
        driver = DummyNodeDriver(0)
        node = Node(id=node_id,
                    name='',
                    state=NodeState.RUNNING,
                    public_ips=[],
                    private_ips=[],
                    driver=driver)
        agentnode = self._get_domain_for_node(node)
        if agentnode is None:
            xml = self._get_persistent_xml(node)
            agentnode = {'id': node_id, 'name': '', 'state': 5, 'extra': {}, 'XMLDesc': xml}
        node = self._from_agent_to_node(agentnode)
        return node

    def _get_volume_paths(self, node):
        xml = self._get_persistent_xml(node)
        return self._get_domain_disk_file_names(xml)

    def ex_create_snapshot(self, node, name):
        diskguids = self._get_volume_paths(node)
        kwargs = {'diskguids': diskguids, 'ovs_connection': self.ovs_connection, 'name': name}
        return self._execute_agent_job('createsnapshots', role='storagedriver', **kwargs)

    def ex_list_snapshots(self, node):
        diskguids = self._get_volume_paths(node)
        kwargs = {'diskguids': diskguids, 'ovs_connection': self.ovs_connection}
        return self._execute_agent_job('listsnapshots', role='storagedriver', **kwargs)

    def ex_delete_snapshot(self, node, timestamp):
        diskguids = self._get_volume_paths(node)
        kwargs = {'diskguids': diskguids, 'ovs_connection': self.ovs_connection, 'timestamp': timestamp}
        return self._execute_agent_job('deletesnapshot', wait=False, role='storagedriver', **kwargs)

    def ex_rollback_snapshot(self, node, timestamp):
        diskguids = self._get_volume_paths(node)
        kwargs = {'diskguids': diskguids, 'timestamp': timestamp, 'ovs_connection': self.ovs_connection}
        return self._execute_agent_job('rollbacksnapshot', role='storagedriver', **kwargs)

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
                        diskfiles.append(ovsdisk.vdiskguid)
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
        diskguids = self._get_domain_disk_file_names(xml, 'disk') + self._get_domain_disk_file_names(xml, 'cdrom')
        self.destroy_volumes_by_guid(diskguids)
        return True

    def ex_limitio(self, volume, iops):
        node = volume.extra['node']
        xmldom = ElementTree.fromstring(self._get_persistent_xml(node))
        devices, disk = self.get_volume_from_xml(xmldom, volume)
        volume.dev = disk.find('target').attrib['dev']
        devices.remove(disk)
        devices.append(ElementTree.fromstring(str(volume)))
        self._set_persistent_xml(node, ElementTree.tostring(xmldom))

        if node.state == LibvirtState.RUNNING:
            return self._execute_agent_job('limitdiskio', queue='hypervisor', machineid=node.id, disks=[volume.id], iops=iops)

    def destroy_volumes_by_guid(self, diskguids):
        kwargs = {'diskguids': diskguids, 'ovs_connection': self.ovs_connection}
        try:
            self._execute_agent_job('deletedisks', role='storagedriver', **kwargs)
        except RuntimeError as rError:
            j.errorconditionhandler.processPythonExceptionObject(
                rError, message="Failed to delete disks may be they are deleted from the storage node")

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

    def ex_stop_node(self, node, force=False):
        machineid = node.id
        return self._execute_agent_job('stopmachine', queue='hypervisor', machineid=machineid, force=force)

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

    def ex_import(self, size, vmid, networkid, disks):
        name = 'vm-%s' % vmid
        volumes = []
        for i, disk in enumerate(disks):
            volume = OpenvStorageVolume(id='%s@%s' % (
                disk['path'], disk['guid']), name='N/A', size=disk['size'], driver=self)
            volume.dev = 'vd%s' % convertnumber(i + 1)
            volumes.append(volume)
        return self._create_node(name, size, networkid=networkid, volumes=volumes)

    def ex_clone_disks(self, diskmapping, snapshotTimestamp=None):
        disks = []
        diskvpool = {}
        for volume, diskname in diskmapping:
            source_edgeclient, edgeclients = self.getEdgeClientFromVolume(volume)
            edgeclient = self.getNextEdgeClient(source_edgeclient['vpool'], edgeclients)
            diskinfo = {'clone_name': diskname,
                        'diskguid': volume.vdiskguid,
                        'storagerouterguid': edgeclient['storagerouterguid']}
            if not snapshotTimestamp is None:
                diskinfo['snapshottimestamp'] = snapshotTimestamp
            diskvpool[volume.vdiskguid] = edgeclient
            disks.append(diskinfo)

        kwargs = {'ovs_connection': self.ovs_connection, 'disks': disks}
        newdisks = self._execute_agent_job('clonedisks', role='storagedriver', **kwargs)
        volumes = []
        for idx, diskinfo in enumerate(disks):
            newdiskguid, vpoolguid = newdisks[idx]
            edgeclient = diskvpool[diskinfo['diskguid']]
            volumeid = self.getVolumeId(newdiskguid, edgeclient, diskinfo['clone_name'])
            volume = OpenvStorageVolume(id=volumeid, name='N/A', size=-1, driver=self)
            volume.dev = 'vd%s' % convertnumber(idx)
            volumes.append(volume)
        return volumes

    def ex_delete_disks(self, volumeguids):
        self._execute_agent_job('deletedisks',
                                role='storagedriver',
                                ovs_connection=self.ovs_connection,
                                diskguids=volumeguids)

    def ex_clone(self, node, size, vmid, networkid, diskmapping, snapshotTimestamp=None):
        name = 'vm-%s' % vmid
        volumes = self.ex_clone_disks(diskmapping, snapshotTimestamp)
        return self. _create_node(name, size, networkid=networkid, volumes=volumes)

    def ex_extend_disk(self, diskguid, newsize, cloudspacegid):
        self._execute_agent_job('extend_disk',
                                role='storagedriver',
                                ovs_connection=self.ovs_connection,
                                size=newsize,
                                diskguid=diskguid)

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
        xmldom = ElementTree.fromstring(xml)
        if xmldom.find('uuid') is None:
            uuid = ElementTree.Element('uuid')
            uuid.text = node.id
            xmldom.append(uuid)
            xml = ElementTree.tostring(xmldom)
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

    def attach_public_network(self, node, vlan):
        """
        Attach Virtual machine to the cpu node public network
        """
        macaddress = self.backendconnection.getMacAddress(self.gid)
        iface = ElementTree.Element('interface')
        iface.attrib['type'] = 'network'
        target = '%s-ext' % (node.name)
        bridgename = self._execute_agent_job('create_external_network', queue='hypervisor', vlan=vlan)
        ElementTree.SubElement(iface, 'source').attrib = {'network': bridgename}
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

    def detach_public_network(self, node):
        xml = self._get_persistent_xml(node)
        dom = ElementTree.fromstring(xml)
        devices = dom.find('devices')
        interfacexml = None
        targetname = '%s-ext' % node.name
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
        memory.text = str(size.ram)
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
