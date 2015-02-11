from libcloud.compute.drivers.openstack import *
from libcloud.compute.drivers.openstack import OpenStackNodeSize
from libcloud.common.openstack import *
from libcloud.compute.types import Provider, NodeState
from libcloud.compute.base import NodeSize, NodeImage, Node
from libcloud.pricing import get_size_price
from datetime import datetime

class DictLikecNodeImage():
    def __init__(self, image):
        self._image = image

    def __getitem__(self, item):
       return getattr(self._image, item)

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
        return DictLikecNodeImage(self.create_image(node, name, {'image_type':'snapshot'}))
    
    def ex_delete_snapshot(self, node, name):
        """
        DELETE IMAGE SNAPSHOT (INSTEAD OF VOLUME SNAPSHOT)
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_delete_snapshot`
        
        :param      node: node to use as a base for image
        :type       node: :class:`Nodeex_delete_snapshot`

        :param      name: name for new image
        :type       name: ``str``

        :rtype: ``bool``
        
        """
        for image in self.list_images():
            if node.id == image.extra['metadata'].get('instance_uuid') and image.name == name:
                return self.delete_image(image)
        return True
    
    
    def _list_snapshots(self, node):
        """
        HELPER FUNCTION
        
        LIST IMAGE SNAPSHOTS (INSTEAD OF VOLUME SNAPSHOTS)
        ADD EPOCH TO IMAGE
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :rtype: ``list :class:NodeImage``
        """
        result = []
        for image in self.list_images():
            if image.extra['metadata'].get('instance_uuid') == node.id and\
                        image.extra['metadata'].get('image_type') == 'snapshot':
                image.epoch = int(datetime.strptime(image.extra['created'], '%Y-%m-%dT%H:%M:%SZ').strftime('%s'))
                result.append(image)
        return result
        
    def ex_list_snapshots(self, node):
        """
        LIST IMAGE SNAPSHOTS (INSTEAD OF VOLUME SNAPSHOTS)
        RETURNS IMAGES AS DICTS
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_list_snapshots`
         
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :rtype: ``list :class:DictLikeNodeImage``
        """
        
        return [{'name':image.name, 'epoch':image.epoch} for image in self._list_snapshots(node)]
    
    def _ex_get_snapshot(self, node, name):
        """
        NEW 
        RETURN SNASHOT
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`
        :param      name: snapshot name
        :type       name: ``str``

        :rtype: ``class: NodeImage``
        """
        for snap in self._list_snapshots(node):
            if snap.name == name:
                return snap
        
    
    def _ex_get_size(self, id):
        """
        NEW 
        RETURN SIZE by ID
        
        :param      id: size ID
        :type       id: ``int``

        :rtype: ``class: NodeSize``
        """
        for s in self.list_sizes():
            if s.id == id:
                return s
    
    def list_sizes(self, location=None):
        """
        RETRUN ALL FLAVORS/SIZES
        
        @overrides :class:`OpenStack_1_1_NodeDriver.ex_list_snapshots`
        """
        sizes = self._to_sizes(
            self.connection.request('/flavors/detail').object)
        
        # make it compatible with libvirt_driver where vcpus are in extra
        for s in sizes:
            s.extra['vcpus'] = s.vcpus
        return sizes
    
    def ex_rollback_snapshot(self, node, name):
        """
        Delete Old instance and use the current snapshot to create a new machine
        returns New Node ID
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`
        :param      name: snapshot name
        :type       name: ``str``


        :rtype: ``str``
        """
        
        node = self.ex_get_node_details(node.id)
        if node.state == self.NODE_STATE_MAP.get('PENDING'):
            raise Exception("Can't rollback a locked machine")

        snap = self._ex_get_snapshot(node, name)
        size = self._ex_get_size( snap.extra['metadata']['instance_type_flavorid'])
        if self.destroy_node(node):
            return self.create_node(name=node.name, image=snap, size=size).id

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
    
    def ex_get_console_url(self, node, length=None):
        """
        Get console url
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_get_console_url`

        :param      node: node
        :type       node: :class:`Node`

        :param      length: Optional number of lines to fetch from the
                            console log
        :type       length: ``int``

        :return: Dictionary with the output
        :rtype: ``dict``
        """

        data = {
            "os-getVNCConsole": {
                "type": "novnc"
            }
        }

        resp = self.connection.request('/servers/%s/action' % node.id,
                                       method='POST', data=data).object
        if resp and 'console' in resp:
            return resp['console'].get('url')
    
    def ex_resume_node(self, node):
        """
        RESUME OPENSTACK NODE
        
        NOTE THAT RESUME ACTION IN OPENSTACK MEANS SOMETHING DIFFERENT THAN
        LIBVIRT [IN LIBVIRT IT MEANS UNPAUSE] THAT IS WHY IT NEEDED TO BE
        OVERRIDEN TO MATCH SAME BEHAVIOR IN LIBVIRT DRIVER
        
        @replaces :class:`OpenStack_1_1_NodeDriver.ex_resume_node`

        :param      node: node
        :type       node: :class:`Node`

        :param      length: Optional number of lines to fetch from the
                            console log
        :type       length: ``int``

        :return: Dictionary with the output
        :rtype: ``dict``
        """

        return self.ex_unpause_node(node)

    def ex_start_node(self, node):
        """
        NEW
        
        START A NODE
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`
        
        :rtype: ``bool``
        
        """
        node = self.ex_get_node_details(node.id)
        # Only start in case of suspended or HALTED [both the same / check NODE_STATE_MAP]
        if node.state in [self.NODE_STATE_MAP.get('SHUTOFF'), self.NODE_STATE_MAP.get('SUSPENDED')]:
            return self.reboot_node(node) # HARD
        return False
    
    # name is create_size to cope with the other call : list_sizes()
    def create_size(self, name, ram, vcpus, disk):
        """
        NEW 
        
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
    def ex_create_template(self, node, name, imageid, snapshotbase=None):
        """
        NEW
        
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
        
        return DictLikecNodeImage(self.create_image(node, name, {'image_type':'image'}))
    
    # This is different from list_images that gets all images including snapshots
    def ex_list_images(self):
        """
        NEW
        
        LIST IMAGAES ONLY & EXCLUDE SNAPSHOTS
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :rtype: ``list``
        """
        result = []
        for image in self.list_images():
            if image.extra['metadata'].get('image_type') == 'snapshot':
                continue
            # make it compatible with libvirt driver as in cloudbroker extra['imagetype'] used
            image.extra['imagetype'] = image.extra['metadata'].get('image_type', 'UNKNOWN')
            result.append(image)
        return result
    
    def ex_stop_node(self, node):
        """
        NEW
        
        STOP NODE
        
        :param      node: node to use as a base for image
        :type       node: :class:`Node`

        :rtype: ``bool``
        """
        return self.ex_suspend_node(node)
    
    def ex_snapshots_can_be_deleted_while_running(self):
        """
        NEW
        FOR OPENSTACK A SNAPSHOT CAN BE DELETED WHILE MACHINE RUNNGIN
        """
        return True