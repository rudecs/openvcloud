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
        edgeinfo = None
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
                edgeinfo = edgeclient
                continue
            edgeclients.append(edgeclient)

        if edgeinfo is None:
            raise exceptions.Error("Could not find storage IP on node %s" % nid)

        def get_vpool_name(host, port):
            for edgeclient in alledgeclients:
                if edgeclient['storageip'] == host and edgeclient['edgeport'] == port:
                    return edgeclient['vpool']
            return None

        def get_vdisk(vdiskguid):
            disks = self.models.disk.search({'referenceId': {'$regex': vdiskguid}})[1:]
            if disks:
                return disks[0]
            return None

        diskguids = driver.client.list_vdisks(edgeinfo['storagerouterguid'])
        while diskguids:
            hasworked = False
            for idx, diskguid in enumerate(diskguids):
                ctx.events.sendMessage("Deactivate Storagerouter", 'Moving Storagerouter on vDisk %s/%s' % (idx+1, len(diskguids)))
                disk = get_vdisk(diskguid)
                if not disk:
                    continue
                hasworked = True
                volume = j.apps.cloudapi.disks.getStorageVolume(disk, driver)
                vpool = get_vpool_name(volume.edgehost, volume.edgeport)
                client = driver.client.getNextEdgeClient(vpool, edgeclients)
                client['vdiskcount'] += 1
                oldloc = "{}:{}".format(volume.edgehost, volume.edgeport)
                newloc = "{}:{}".format(client['storageip'], client['edgeport'])
                disk.referenceId = disk.referenceId.replace(oldloc, newloc)
                kwargs = {
                    'storagerouterguid': client['storagerouterguid'],
                    'ovs_connection': driver.client.ovs_connection,
                    'diskguid': volume.vdiskguid
                }
                driver.client._execute_agent_job('move_disk', role='storagemaster', **kwargs)
            if not hasworked:
                break
            diskguids = driver.client.list_vdisks(edgeinfo['storagerouterguid'])

        ctx.events.sendMessage("Deactivate Storagerouter", 'Finished moving all vdisks', 'success')
        return "Finished Deactivating Storagerouter"
