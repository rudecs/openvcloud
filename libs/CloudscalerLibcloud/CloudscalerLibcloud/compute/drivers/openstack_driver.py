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
        Originally known as ex_list_snapshots
        """
        return self._to_volume_snapshots(
            self.connection.request('/os-snapshots').object)

    def ex_create_volume_snapshot(self, volume, name, description=None, force=False):
        """
        Originally known as ex_create_snapshot
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
        Originally known as ex_delete_snapshot
        """
        resp = self.connection.request('/os-snapshots/%s' % snapshot.id,
                                       method='DELETE')
        return resp.status == httplib.NO_CONTENT
    
    def ex_create_volume_snapshot(self, volume, name, description=None, force=False):
        """
        Originally known as ex_create_snapshot
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
        Overriden behavior to create image snapshots
        """
        return self.create_image(node, name, {'image_type':'snapshot'})
    
    def ex_delete_snapshot(self, node, name):
        """
        Overriden behavior to delete image snapshots
        """
        for image in self.list_images():
            if node.id == image.extra['metadata'].get('instance_uuid') and image.name == name:
                return self.delete_image(image)
        return True
    
    def ex_list_snapshots(self, node):
        """
        Overriden behavior to list image snapshots
        Also return type is changed from ImageNode to dict to match the
        Libvirt behavior
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
        Originally known as  _to_snapshot
        """
        return self._to_snapshot(data)
    
    def _to_volume_snapshots(self, obj):
        """
          Originally known as  _to_volume_snapshots
        """
        return self._to_snapshots(obj)
    
    def ex_start_node(self, node):
        """
        NEW
        """
        # Only start in case of suspended or SHUTOFF [both the same / check NODE_STATE_MAP]
        if self.NODE_STATE_MAP[self.node.state] in [self.NODE_STATE_MAP['SHUTOFF'], self.NODE_STATE_MAP['SUSPENDED']]:
            return self.reboot_node(node) # HARD
        return False