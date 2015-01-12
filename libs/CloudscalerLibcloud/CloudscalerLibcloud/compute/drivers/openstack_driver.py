from libcloud.compute.drivers.openstack import *
from libcloud.compute.drivers.openstack import OpenStackNodeSize
from libcloud.common.openstack import *
from libcloud.compute.types import Provider, NodeState
from libcloud.compute.base import NodeSize, NodeImage, Node
from libcloud.pricing import get_size_price
from datetime import datetime

class OpenStackNodeDriver(OpenStack_1_1_NodeDriver):

    def ex_list_volume_snapshots(self):
        """
        LIST VOLUME SNAPSHOTS
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_list_snapshots`
         
        :rtype: ``list``
        """
        return self._to_volume_snapshots(
            self.connection.request('/os-snapshots').object)

    def ex_create_volume_snapshot(self, volume, name, description=None, force=False):
        """
        CREATE VOLUME SNAPSHOT
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_create_snapshot`
        
        :param      volume: volume
        :type       volume: :class:`StorageVolume`

        :keyword    name: New name for the volume snapshot
        :type       name: ``str``

        :keyword    description: Description of the snapshot (optional)
        :type       description: ``s:class:`NodeImage`tr``

        :keyword    force: Whether to force creation (optional)
        :type       force: ``bool``

        :rtype:     :class:`VolumeSnapshot`
        """
        
        data = {'snapshot': {'display_name': name,
                             'display_description': description,
                             'volume_id': volume.id,
                             'force': force}}

        return self._to_volume_snapshot(self.connection.request('/os-snapshots',
                                                         method='POST',
                                                         data=data).object)
    def ex_delete_volume_snapshot(self, snapshot):
        """
        DELETE VOLUME SNAPSHOT
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_delete_snapshot`

        :param      snapshot: snapshot
        :type       snapshot: :class:`VolumeSnapshot`

        :rtype:     ``bool``
        """
        resp = self.connection.request('/os-snapshots/%s' % snapshot.id,
                                       method='DELETE')
        return resp.status == httplib.NO_CONTENT
    
    def ex_create_volume_snapshot(self, volume, name, description=None, force=False):
        """
        
        CREATE VOLUME SNAPSHOT
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_create_snapshot`
        
        :param      volume: volume
        :type       volume: :class:`StorageVolume`

        :keyword    name: New name for the volume snapshot
        :type       name: ``str``

        :keyword    description: Description of the snapshot (optional)
        :type       description: ``str``

        :keyword    force: Whether to force creation (optional)
        :type       force: ``bool``

        :rtype:     :class:`VolumeSnapshot`

        """
        data = {'snapshot': {'display_name': name,
                             'display_description': description,
                             'volume_id': volume.id,
                             'force': force}}

        return self._to_volume_snapshot(self.connection.request('/os-snapshots',
                                                         method='POST',
                                                         data=data).object)

    def ex_create_snapshot(self, node, name, snapshottype=None):
        """
        CREATE IMAGE SNAPSHOT (INSTEAD OF VOLUME SNAPSHOT)
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_create_snapshot`
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :param      name: name for new image
        :type       name: ``str``

        :rtype: :class:`NodeImage`
        
        """
        return self.create_image(node, name, {'image_type':'snapshot'})
    
    def ex_delete_snapshot(self, node, name):
        """
        DELETE IMAGE SNAPSHOT (INSTEAD OF VOLUME SNAPSHOT)
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_delete_snapshot`
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :param      name: name for new image
        :type       name: ``str``

        :rtype: ``bool``
        
        """
        for image in self.list_images():
            if node.id == image.extra['metadata'].get('instance_uuid') and image.name == name:
                return self.delete_image(image)
        return True
    
    def ex_list_snapshots(self, node):
        """
        LIST IMAGE SNAPSHOTS (INSTEAD OF VOLUME SNAPSHOTS)
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_list_snapshots`
         
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :rtype: ``list``
        """
        result = []
        for image in self.list_images():
            if image.extra['metadata'].get('instance_uuid') == node.id and\
                        image.extra['metadata'].get('image_type') == 'snapshot':
                
                snap = {'name': image.name,
                    'epoch': int(datetime.strptime(image.extra['created'], '%Y-%m-%dT%H:%M:%SZ').strftime('%s')) }
                result.append(snap)
        return result
    
    def ex_rollback_snapshot(self, node, name):
        """
        Not supported in open stack
        """
        raise NotImplementedError(" Not supported in open stack")

    def _to_volume_snapshot(self, data):
        """
        HELPER FUNCTION (NOT USED DIRECTLY)
        
        @replaces :class:`OpenStack_1_1_NodeDriver._to_snapshot`
        """
        return self._to_snapshot(data)
    
    def _to_volume_snapshots(self, obj):
        """
        HELPER FUNCTION (NOT USED DIRECTLY)
        
        @replaces :class:`OpenStack_1_1_NodeDriver._to_snapshots`
        """
        return self._to_snapshots(obj)
    
    def ex_start_node(self, node):
        """
        START A NODE
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`
        
        :rtype: ``bool``
        
        """
        # Only start in case of suspended or SHUTOFF [both the same / check NODE_STATE_MAP]
        if self.NODE_STATE_MAP[self.node.state] in [self.NODE_STATE_MAP['SHUTOFF'], self.NODE_STATE_MAP['SUSPENDED']]:
            return self.reboot_node(node) # HARD
        return False

    def create_size(self, name, ram, vcpus, disk):
        """
        CREATE A FLAVTOR
        
        IF SUCCESSFUL, RETURNS NELY CREATED FLAVOR
        
        :param      name: flavor name
        :type       name: : ``str``
        
        :param      ram: RAM size in MBs
        :type       ram: : ``int``
        
        :param      vcpus: number of virtual cpus
        :type       vcpus: : ``int``
        
        :param      disk: DISK size in GBs
        :type       disk: : ``int``
        
        :rtype: ``bool``
        """
        
        data = {
            "flavor": {
                "name": name,
                "ram": ram,
                "vcpus": vcpus,
                "disk": disk
            }
        }

        return self.connection.request('/flavors',
                                       method='POST',
                                       data=data).object
    
    # IS THER AWAY TO CREATE IMAGE FROM ANOTHER IMAGE IN OPENSTACK?
    def ex_createTemplate(self, node, name, imageid, snapshotbase=None):
        """
        CREATES AN IMAGE FROM THE NODE 
        IGNORES imageid
        
        :param      node: class: Node
        :type       node: : ``Node``
        
        :param      name: Image name
        :type       name: : ``str``
        
        :param      imageid: IGNORED
        :type       imageid: : ``str``
        
        
        :rtype: ``class: NodeImage``
        """
        return self.create_image(node, name, {'image_type':'image'})
