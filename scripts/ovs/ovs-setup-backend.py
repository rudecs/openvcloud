from JumpScale import j
import requests
import random
import string
import sys
import time

from ovs.dal.lists.backendlist import BackendList
from ovs.dal.lists.backendtypelist import BackendTypeList
from ovs.dal.hybrids.backend import Backend

from ovs.extensions.storage.volatilefactory import VolatileFactory
from ovs.dal.lists.storagerouterlist import StorageRouterList
from ovs.dal.hybrids.storagerouter import StorageRouter
from ovs.dal.datalist import DataList
from ovs.dal.dataobjectlist import DataObjectList
from ovs.lib.storagerouter import StorageRouterController
from ovs.lib.storagedriver import StorageDriverController
from ovs.lib.mdsservice import MDSServiceController
from ovs.lib.disk import DiskController

from ovs.dal.hybrids.albabackend import AlbaBackend
from ovs.lib.albanodecontroller import AlbaNodeController
from ovs.lib.albacontroller import AlbaController
from ovs.dal.lists.albanodelist import AlbaNodeList

# internal stuff
requests.packages.urllib3.disable_warnings()

# environment
ovs = j.application.getAppInstanceHRD(name='openvstorage', instance='main', domain='openvcloud')
environment = ovs.getStr('instance.clustername')
print '[+] setup environment: %s' % environment

"""
backends = BackendList.get_backends()
x = backends[0]
AlbaController.remove_cluster(x.alba_backend_guid)

disks = x.alba_backend.all_disks
for disk in disks:
    if disk['status'] == 'claimed':
        print disk['asd_id']
        AlbaController.remove_units(x.alba_backend_guid, [disk['asd_id']])


sys.exit(0)
"""

def dump():
    print '[+] storage map detected:'
    
    routers = StorageRouterList.get_storagerouters()
    
    for router in routers:
        print '[+] %s: %s' % (router.name, router.status)
        
        disks = router.disks
        
        for disk in disks:
            print '[+] +--+ /dev/%s (SSD: %s, Size: %.1f GB)' % (disk.name, disk.is_ssd, (disk.size / (1024 * 1024 * 1024)))
            
            parts = disk.partitions
            
            for part in parts:
                print '[+]    +-- %-20s (%.1f GB)' % (part.mountpoint, part.size / (1024 * 1024 * 1024))
    
        print ''

"""
Set roles on disks
"""
def disks():
    print '[+] setting storage router partitions roles'
    
    # partition manager
    def _part(part):
        updated = False
        
        roles = {
            "/mnt/ovs-db-write": ["DB", "WRITE"],
            "/mnt/ovs-read": ["READ"],
            "/var/tmp": ["SCRUB"]
        }
        
        # add roles if there is no one already
        if part.folder in ["/mnt/ovs-db-write", "/mnt/ovs-read", "/var/tmp"]:
            if part.roles:
                print '[+] %s: already set: %s' % (part.folder, part.roles)
                
            else:
                # print '[+] setting up %s: %s' % (part.folder, roles[part.folder])
                part.roles = roles[part.folder]
                updated = True
        
        return updated
    
    # partitions list
    def _parts(parts):
        updated = False
        
        for part in parts:
            if _part(part):
                updated = True
                part.save()
        
        return updated
    
    # disks list    
    def _disks(disks):
        updated = False
        
        for disk in disks:
            if _parts(disk.partitions):
                updated = True
                disk.save()
        
        return updated
    
    # routers list
    commits = 0
    routers = StorageRouterList.get_storagerouters()
    for router in routers:        
        if _disks(router.disks):
            print '[+] commit storage router: %s' % router.name
            router.save()
            commits += 1
    
    return commits

"""
Create alba backend
"""
def backend(name):
    backends = BackendList.get_backends()
    albaback = None
    
    for backend in backends:
        if backend.name == name:
            albaback = backend.guid
    
    if albaback is None:
        alba = Backend()
        type = BackendTypeList.get_backend_type_by_code('alba')
        
        alba.name = name
        alba.backend_type = type
        alba.save()
        
        alba_backend = AlbaBackend(alba.alba_backend_guid)
        alba_backend.backend = alba
        alba_backend.backend.status = 'INSTALLING'
        alba_backend.backend.save()
        alba_backend.save()
        
        print '[+] creating backend, this will take some times'
        AlbaController.add_cluster(alba_backend.guid)
        
        albaback = alba_backend.guid
    
    return albaback

def initialize(disks):
    for disk in disks:
        if disk['status'] == 'available' or disk['status'] == 'claimed':
            print '[+] skipping %s: disk %s' % (disk['device'], disk['status'])
            continue
            
        if disk['status'] != 'uninitialized':
            print '[-] skipping %s: disk not uninitialized (%s)' % (disk['device'], disk['status'])
            continue
        
        # initializing
        node = AlbaNodeList.get_albanode_by_node_id(disk['node_id'])
        print '[+] initializing: %s, %s ' % (disk['name'], node.guid)
        
        AlbaNodeController.initialize_disks(node.guid, [disk['name']])

def claim(disks, alba):
    for disk in disks:
        if disk['status'] != 'available':
            print '[+] skipping %s: disk not available' % disk['device']
            continue
        
        node = AlbaNodeList.get_albanode_by_node_id(disk['node_id'])
        
        print '[+] claiming: %s' % disk['asd_id']
        AlbaController.add_units(alba.guid, {disk['asd_id']: node.guid})

def initializer(name):
    alba = None
    
    back = BackendList.get_by_name(name)
    alba = back.alba_backend
    
    if not alba.available:
        print '[-] alba not ready, please check'
        return None
    
    # print alba.all_disks
    
    print '[+] alba ready, initializing disks'
    initialize(alba.all_disks)
    
    print '[+] claiming disks'
    claim(alba.all_disks, alba)
    
    print '[+] checking disks'
    
    for disk in alba.all_disks:
        if disk['status'] != 'claimed':
            print '[-] %s: not claimed: %s' % (disk['name'], disk['status'])
    
    print '[+] backend initialized and ready'
    
    return True

def remove_first_backend():
    backends = BackendList.get_backends()
    x = backends[0]
    AlbaController.remove_cluster(x.alba_backend_guid)


print '[+] setting up disks roles'
commits = disks()

print '[+] waiting for disks to be synced: %d disks' % commits
time.sleep(commits)

alba = backend(environment)
print '[+] backend guid: %s' % alba

time.sleep(2)

initializer(environment)

# AlbaController.remove_cluster(<the guid>)

# Add preset
"""
# Create new preset
presetfile = '/opt/openvstorage/alba-openvcloud.json'
configfile = '/opt/OpenvStorage/config/arakoon/%s-abm/%s-abm.cfg' % (environment, environment)

nodename = ovs.getStr('instance.ovs.masternode')
print '[+] node: %s, environment: %s' % (nodename, environment)

node = j.atyourservice.get(name='node.ssh', instance=nodename)

node.execute('alba create-preset alba-openvcloud --config %s < %s' % (configfile, presetfile))
node.execute('alba preset-set-default alba-openvcloud --config %s' % configfile)
"""

# Create vpool
# Add nodes to vpool
