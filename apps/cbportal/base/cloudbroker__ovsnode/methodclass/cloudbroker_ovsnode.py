from JumpScale import j
from xml.etree import ElementTree
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor


class cloudbroker_ovsnode(BaseActor):
    def __init__(self):
        super(cloudbroker_ovsnode, self).__init__()
        self.scl = j.clients.osis.getNamespace('system')
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        self.lcl = j.clients.osis.getNamespace('libcloud')

    def activateNodes(self, nids, **kwargs):
        return self.scl.node.updateSearch({'id': {'$in': nids}}, {'$set': {'active': True}})

    def deactivateNodes(self, nids, **kwargs):
        if len(nids) != 1:
            raise exceptions.BadRequest("Can only deactivate 1 Storagerouter at a time")
        nid = nids[0]
        ctx = kwargs['ctx']
        node = self.scl.node.get(nid)
        node.active = False
        self.scl.node.set(node)
        storageip = None
        myips = []
        for nic in node.netaddr:
            myips.extend(nic["ip"])

        if 'storagedriver' not in node.roles:
            raise exceptions.BadRequest('Node with nid %s is not a storagedriver' % nid)

        driver = self.cb.getProviderByGID(node.gid)
        alledgeclients = driver.client.all_edgeclients[:]
        edgeclients = []
        for edgeclient in alledgeclients:
            if edgeclient['storageip'] in myips:
                storageip = edgeclient['storageip']
                continue
            edgeclients.append(edgeclient)

        if storageip is None:
            raise exceptions.Error("Could not find storage IP on node %s" % nid)

        def get_vpool_name(host, port):
            for edgeclient in alledgeclients:
                if edgeclient['storageip'] == host and edgeclient['edgeport'] == port:
                    return edgeclient['vpool']
            return None

        query = {
            '$query': {
                'gid': node.gid,
                'status': {'$ne': 'DESTROYED'},
            },
            '$fields': ['id']
        }
        cloudspaces = [cs['id'] for cs in self.models.cloudspace.search(query, size=0)[1:]]

        query = {
            '$query': {
                'status': {'$ne': 'DESTROYED'},
                'cloudspaceId': {'$in': cloudspaces}
            },
            '$fields': ['referenceId', 'id', 'disks']
        }

        requireschanges = []
        for vm in self.models.vmachine.search(query, size=0)[1:]:
            node = self.cb.Dummy(id=vm['referenceId'])
            xml = driver.client._get_persistent_xml(node)
            if storageip in xml:
                vm['xml'] = xml
                vm['node'] = node
                requireschanges.append(vm)

        for idx, vm in enumerate(requireschanges):
            ctx.events.sendMessage("Deactivate Storagerouter", 'Moving Storagerouter on Virtual Machine %s/%s' % (idx+1, len(requireschanges)))
            node = vm['node']
            xml = vm['xml']
            xmldom = ElementTree.fromstring(xml)
            for diskid in vm['disks']:
                disk = self.ccl.disk.get(diskid)
                if storageip in disk.referenceId:
                    volume = j.apps.cloudapi.disks.getStorageVolume(disk, driver)
                    vpool = get_vpool_name(volume.edgehost, volume.edgeport)
                    client = driver.client.getNextEdgeClient(vpool, edgeclients)
                    client['vdiskcount'] += 1
                    oldloc = "{}:{}".format(volume.edgehost, volume.edgeport)
                    newloc = "{}:{}".format(client['storageip'], client['edgeport'])
                    disk.referenceId = disk.referenceId.replace(oldloc, newloc)
                    self.ccl.disk.set(disk)
                    devices, xmldisk = driver.client.get_volume_from_xml(xmldom, volume)
                    if xmldisk is not None:
                        host = xmldisk.find('source/host')
                        host.attrib['name'] = client['storageip']
                        host.attrib['port'] = str(client['edgeport'])
                    kwargs = {
                        'storagerouterguid': client['storagerouterguid'],
                        'ovs_connection': driver.client.ovs_connection,
                        'diskguid': volume.vdiskguid
                    }
                    driver.client._execute_agent_job('move_disk', role='storagemaster', **kwargs)

            for source in xmldom.findall('devices/disk/source'):
                host = source.find('host')
                if host.attrib['name'] == storageip:
                    vpool = get_vpool_name(storageip, int(host.attrib['port']))
                    client = driver.client.getNextEdgeClient(vpool, edgeclients)
                    client['vdiskcount'] += 1
                    host.attrib['name'] = client['storageip']
                    host.attrib['port'] = str(client['edgeport'])
                    devicename = '/{}.raw'.format(source.attrib['name'])
                    kwargs = {
                        'storagerouterguid': client['storagerouterguid'],
                        'ovs_connection': driver.client.ovs_connection,
                        'devicename': devicename
                    }
                    driver.client._execute_agent_job('move_disk', role='storagemaster', **kwargs)

            xml = ElementTree.tostring(xmldom)
            driver.client._set_persistent_xml(node, xml)

        ctx.events.sendMessage("Deactivate Storagerouter", 'Finished moving all vdisks', 'success')
        return "Finished Deactivating Storagerouter"
