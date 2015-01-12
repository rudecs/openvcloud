#Add extra specific cloudscaler functions for libvirt libcloud driver

from CloudscalerLibcloud.utils import connection, routeros
from libcloud.compute.base import NodeImage, NodeSize, Node, NodeState
from jinja2 import Environment, PackageLoader
from JumpScale.baselib.dnsmasq import DNSMasq
from xml.etree import ElementTree
import urlparse
import json
import os
import crypt, random
import time
from JumpScale import j

BASEPOOLPATH = '/mnt/vmstor/'
IMAGEPOOL = '/mnt/vmstor/templates'



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

    def __init__(self, id, gid, uri):
        self._rndrbn_vnc = 0
        self.id = id
        self.gid = gid
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
            extra={'vcpus': size['vcpus']},
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

    def _execute_agent_job(self, name_, id=None, wait=True, queue=None, **kwargs):
        if not id:
            id = int(self.id)
        else:
            id = int(id)
        job = self.backendconnection.agentcontroller_client.executeJumpscript('cloudscalers', name_, nid=id, gid=self.gid, wait=wait, queue=queue, args=kwargs)
        if wait and job['state'] != 'OK':
            if job['state'] == 'NOWORK':
                raise RuntimeError('Could not find agent with nid:%s' %  id)
            if job['result']:
                raise RuntimeError("Could not execute %s for nid:%s, error was:%s"%(name_,id,job['result']))
        if wait:
            return job['result']
        else:
            return job


    def _create_disk(self, vm_id, size, image, disk_role='base'):
        disktemplate = self.env.get_template("disk.xml")
        diskname = vm_id + '-' + disk_role + '.qcow2'
        diskbasevolume = image.extra['path']
        disksize = size.disk
        diskbasevolumepath = IMAGEPOOL + '/' + diskbasevolume
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolumepath, 'disksize': disksize})

        poolname = vm_id
        self._execute_agent_job('createdisk', diskxml=diskxml, poolname=poolname)
        return diskname

    def _create_clone_disk(self, vm_id, size, clone_disk, disk_role='base'):
        disktemplate = self.env.get_template("disk.xml")
        diskname = vm_id+ '-' + disk_role + '.qcow2'
        diskbasevolume = clone_disk
        diskxml = disktemplate.render({'diskname': diskname, 'diskbasevolume':
                                       diskbasevolume, 'disksize': size.disk})
        poolname = vm_id
        self._execute_agent_job('createdisk', queue='hypervisor', diskxml=diskxml, poolname=poolname)
        return diskname

    def _create_metadata_iso(self, name, userdata, metadata, type):
        return self._execute_agent_job('createmetaiso', queue='hypervisor', name=name, poolname=name, metadata=metadata, userdata=userdata, type=type)

    def generate_password_hash(self, password):
        def generate_salt():
            salt_set = ('abcdefghijklmnopqrstuvwxyz'
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                        '0123456789./')
            salt = 16 * ' '
            return ''.join([random.choice(salt_set) for c in salt])
        salt = generate_salt()
        return crypt.crypt(password, '$6$' + salt)


    def create_node(self, name, size, image, location=None, auth=None, networkid=None):
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
            #At this moment we handle only NodeAuthPassword
            password = auth.password
            if image.extra['imagetype'] not in ['WINDOWS', 'Windows']:
                userdata = {'password': password, 'users': [{'name':'cloudscalers', 'plain_text_passwd': password, 'lock-passwd': False, 'shell':'/bin/bash', 'sudo':'ALL=(ALL) ALL'}], 'ssh_pwauth': True, 'chpasswd': {'expire': False }}
                metadata = {'local-hostname': name}
            else:
                userdata = {}
                metadata = {'admin_pass': password, 'hostname': name}
            metadata_iso = self._create_metadata_iso(name, userdata, metadata, image.extra['imagetype'])
        diskname = self._create_disk(name, size, image)
        if not diskname or diskname == -1:
            #not enough free capcity to create a disk on this node
            return -1
        return self._create_node(name, diskname, size, metadata_iso, networkid)

    def _create_node(self, name, diskname, size, metadata_iso=None, networkid=None):
        machinetemplate = self.env.get_template("machine.xml")
        vxlan = '%04x' % networkid 
        macaddress = self.backendconnection.getMacAddress(self.gid)
        POOLPATH = '%s/%s' % (BASEPOOLPATH, name)
        
        result = self._execute_agent_job('createnetwork', queue='hypervisor', networkid=networkid)
        if not result or result == -1:
            return -1

        networkname = result['networkname']
        
        if not metadata_iso:
            machinexml = machinetemplate.render({'machinename': name, 'diskname': diskname, 'vxlan': vxlan,
                                             'memory': size.ram, 'nrcpu': size.extra['vcpus'], 'macaddress': macaddress, 'network': networkname, 'poolpath': POOLPATH})
        else:
            machinetemplate = self.env.get_template("machine_iso.xml")
            machinexml = machinetemplate.render({'machinename': name, 'diskname': diskname, 'isoname': metadata_iso, 'vxlan': vxlan,
                                             'memory': size.ram, 'nrcpu': size.extra['vcpus'], 'macaddress': macaddress, 'network': networkname, 'poolpath': POOLPATH})


        # 0 means default behaviour, e.g machine is auto started.

        result = self._execute_agent_job('createmachine', queue='hypervisor', machinexml=machinexml)
        if not result or result == -1:
            #Agent is not registered to agentcontroller or we can't provision the machine(e.g not enough resources, delete machine)
            if result == -1:
                self._execute_agent_job('deletevolume', queue='hypervisor', path=os.path.join(POOLPATH, diskname))
            return -1

        vmid = result['id']
        #dnsmasq = DNSMasq()
        #nsid = '%04d' % networkid
        #namespace = 'ns-%s' % nsid
        #config_path = j.system.fs.joinPaths(j.dirs.varDir, 'vxlan',nsid)
        #dnsmasq.setConfigPath(nsid, config_path)
        self.backendconnection.registerMachine(vmid, macaddress, networkid)
        #dnsmasq.addHost(macaddress, ipaddress,name)
        ipaddress = 'Undefined'
        node = self._from_agent_to_node(result, ipaddress)
        self._set_persistent_xml(node, result['XMLDesc'])
        return node

    def ex_createTemplate(self, node, name, imageid, snapshotbase=None):
        domain = self._get_domain_for_node(node=node)
        self._execute_agent_job('createtemplate', wait=False, queue='io', machineid=node.id, templatename=name, createfrom=snapshotbase, imageid=imageid)
        return True

    def ex_get_node_details(self, node_id):
        node = Node(id=node_id)
        node = self._from_agent_to_node(self._get_domain_for_node(node))
        backendnode = self.backendconnection.getNode(node.id)
        node.extra['macaddress'] = backendnode['macaddress']
        return node

    def ex_create_snapshot(self, node, name, snapshottype='external'):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain['XMLDesc'])
        diskfiles = self._get_domain_disk_file_names(xml)
        t = int(time.time())
        POOLPATH = '%s/%s' % (BASEPOOLPATH, domain['name'])
        snapshot = self.env.get_template('snapshot.xml').render(name=name, diskfiles=diskfiles, type=snapshottype, time=t, poolpath=POOLPATH)
        return self._execute_agent_job('snapshot', queue='hypervisor', machineid=node.id, snapshottype=snapshottype, xml=snapshot)

    def ex_list_snapshots(self, node):
        return self._execute_agent_job('listsnapshots', queue='default', machineid=node.id)

    def ex_delete_snapshot(self, node, name):
        return self._execute_agent_job('deletesnapshot', wait=False, queue='io', machineid=node.id, name=name)

    def ex_rollback_snapshot(self, node, name):
        return self._execute_agent_job('rollbacksnapshot', queue='hypervisor', machineid=node.id, name=name)

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
                    if 'dev' in source.attrib:
                        diskfiles.append(source.attrib['dev'])
                    if 'file' in source.attrib:
                        diskfiles.append(source.attrib['file'])
        return diskfiles

    def _get_snapshot_disk_file_names(self, xml):
        xml = ElementTree.fromstring(xml)
        domain = xml.findall('domain')[0]
        return self._get_domain_disk_file_names(domain)

    def destroy_node(self, node):
        #dnsmasq = DNSMasq()
        backendnode = self.backendconnection.getNode(node.id)
        #nsid = '%04d' % backendnode['networkid']
        #namespace = 'ns-%s' % nsid
        #config_path = j.system.fs.joinPaths(j.dirs.varDir, 'vxlan',nsid)
        #dnsmasq.setConfigPath(nsid, config_path)
        #dnsmasq.removeHost(backendnode['macaddress'])
        self.backendconnection.unregisterMachine(node.id)
        job = self._execute_agent_job('deletemachine',queue='hypervisor', machineid = node.id)
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

    def ex_shutdown(self, node):
        machineid = node.id
        return self._execute_agent_job('stopmachine', queue='hypervisor', machineid = machineid)

    def ex_suspend_node(self, node):
        machineid = node.id
        return self._execute_agent_job('suspendmachine', queue='hypervisor', machineid = machineid)

    def ex_resume_node(self, node):
        machineid = node.id
        return self._execute_agent_job('resumemachine', queue='hypervisor', machineid = machineid)


    def ex_pause_node(self, node):
        machineid = node.id
        return self._execute_agent_job('pausemachine', queue='hypervisor', machineid = machineid)


    def ex_unpause_node(self, node):
        machineid = node.id
        return self._execute_agent_job('unpausemachine', queue='hypervisor', machineid = machineid)
    

    def ex_soft_reboot_node(self, node):
        machineid = node.id
        return self._execute_agent_job('softrebootmachine', queue='hypervisor', machineid = machineid)


    def ex_hard_reboot_node(self, node):
        machineid = node.id
        return self._execute_agent_job('hardrebootmachine', queue='hypervisor', machineid = machineid)

    def ex_start_node(self, node):
        backendnode = self.backendconnection.getNode(node.id)
        networkid = backendnode['networkid']
        xml = self._get_persistent_xml(node)
        machineid = node.id 
        result = self._execute_agent_job('createnetwork', queue='hypervisor', networkid=networkid)
        if not result or result == -1:
            return -1
        return self._execute_agent_job('startmachine', queue='hypervisor', machineid = machineid, xml = xml)    
 
    def ex_get_console_output(self, node):
        domain = self._get_domain_for_node(node=node)
        xml = ElementTree.fromstring(domain['XMLDesc'])
        graphics = xml.find('devices/graphics')
        info = dict()
        info['port'] = int(graphics.attrib['port'])
        info['type'] = graphics.attrib['type']
        info['ipaddress'] = self._get_connection_ip()
        return info

    def ex_clone(self, node, size, name):
        snap = self.ex_create_snapshot(node, None, 'external')
        snapname = snap['name']
        snapxml = snap['xml']
        diskname = self._get_snapshot_disk_file_names(snapxml)[0]
        #diskname = os.path.basename(diskname)
        clone_diskname = self._create_clone_disk(name, size, diskname)
        return self._create_node(name, clone_diskname, size)

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
        return self._execute_agent_job('getmachine', queue='default', machineid = node.id)

    def _from_agent_to_node(self, domain, publicipaddress=''):
        state = self.NODE_STATE_MAP.get(domain['state'], NodeState.UNKNOWN)
        extra = domain['extra']
        node = Node(id=domain['id'], name=domain['name'], state=domain['state'],
                    public_ips=[publicipaddress], private_ips=[], driver=self,
                    extra=extra)
        return node


