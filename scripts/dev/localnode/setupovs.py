#!/usr/bin/env python2
from JumpScale import j
import json
import time
import os
import stat

def get_loop_devices():
    hostname = j.system.net.getHostname()
    _, output = j.system.process.execute('losetup -J')
    devices = {}
    for device in json.loads(output)['loopdevices']:
        if hostname in device['back-file']:
            devices[os.path.basename(device['back-file']).split('-')[1]] = os.path.basename(device['name'])
    return devices


def get_major_minor(device):
    try:
        stat = os.lstat(device)
        return os.major(stat.st_rdev), os.minor(stat.st_rdev)
    except:
        return 0, 0

def checkdisk(disk):
    devpath = '/dev/{}'.format(disk['name'])
    major, minor = get_major_minor(devpath)
    if "{}:{}".format(major, minor) != disk['maj:min']:
        if major != 0:
            os.unlink(devpath)
        major, minor = disk['maj:min'].split(':')
        major, minor = int(major), int(minor)
        os.mknod(devpath, stat.S_IFBLK, os.makedev(major, minor))

def recreateloop():
    _, output = j.system.process.execute('lsblk -J')
    for disk in json.loads(output)['blockdevices']:
        checkdisk(disk)
        for child in disk.get('children', []):
            checkdisk(child)


scl = j.clients.osis.getNamespace('system')
ovs = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']
ovscl = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))
storagerouterguid = ovscl.get('/storagerouters', )['data'][0]
recreateloop()
devices = get_loop_devices()

diskinfo = ovscl.get('/disks', params={'storagerouterguid': storagerouterguid, 'contents': '_relations'})
for disk in diskinfo['data']:
    if disk['name'] == devices['db']:
        break
else:
    raise RuntimeError('Can not find loop0 disk')

print('Creating roles')
addrolesdata = {"size":3998220288,"offset":1048576,"disk_guid":disk['guid'],"partition_guid":disk['partitions_guids'][0],"roles":["DB","DTL","SCRUB","WRITE"]}
ovscl.post('/storagerouters/{}/configure_disk'.format(storagerouterguid), data=json.dumps(addrolesdata))

for backendtype in ovscl.get('/backendtypes/', params={'contents': ''})['data']:
    if backendtype['code'] == 'alba':
        break
else:
    raise RuntimeError('Could not find alba backend type')

print('Creating backend')
createbackenddata = {"name":"mybackend","backend_type_guid":backendtype['guid']}
backendguid = ''
backendguid = ovscl.post('/backends/', data=json.dumps(createbackenddata))['guid']
albabackenddata = {"backend_guid":backendguid,"scaling":"LOCAL"}
albabackendguid = ''
albabackendguid = ovscl.post('/alba/backends/', data=json.dumps(albabackenddata))['guid']
time.sleep(5)

while True:
    info = ovscl.get('/alba/backends/{}/'.format(albabackendguid), params={'contents': '_dynamics,_relations'})
    if info['live_status'] == 'running':
        break
    print('Waiting for backend to be running')
    time.sleep(5)

print('Update presets')
presetdata = {"name":"default","policies":[[1,1,1,1]]}
ovscl.post('/alba/backends/{}/update_preset/'.format(albabackendguid), data=json.dumps(presetdata))

nodeguid = ovscl.get('/alba/nodes/')['data'][0]
print('Initialize alba disks')
initializediskdata = {"disks":{"/dev/{}".format(devices['asd']):1}}
taskguid = ovscl.post('/alba/nodes/{}/initialize_disks/'.format(nodeguid), data=json.dumps(initializediskdata))
task = ovscl.wait_for_task(taskguid, timeout=30)
if not task[0]:
    print('Fixing loops')
    recreateloop()
    taskguid = ovscl.post('/alba/nodes/{}/initialize_disks/'.format(nodeguid), data=json.dumps(initializediskdata))
    task = ovscl.wait_for_task(taskguid, timeout=30)
    if not task[0]:
        raise RuntimeError(task[1])

def get_asd_info():
    backenddata = ovscl.get('/alba/backends/{}/'.format(albabackendguid), params={'contents': '_dynamics,-statistics.-ns_data._relations'})['local_stack']
    for nodeid, stackdata in backenddata.items():
        for devname, devdata in stackdata.items():
            if devname == devices['asd']:
                return devdata['guid'], devdata['asds'].keys()[0]


asdinfo = get_asd_info()
if not asdinfo:
    raise RuntimeError('Failed to get asd info')
claimasddata = {"osds":{asdinfo[1]: asdinfo[0]}}
print('Claiming ASD')
taskguid = ovscl.post('/alba/backends/{}/add_units/'.format(albabackendguid), data=json.dumps(claimasddata))
ovscl.wait_for_task(taskguid, 20)

print('Creating pool')
createpooldata = {"call_parameters":{"vpool_name":"vmstor","connection_info":{"host":"","port":80,"local":True,"client_id":"","client_secret":""},"backend_info":{"preset":"default","alba_backend_guid":albabackendguid},"storage_ip":"172.17.1.10","storagerouter_ip":"172.17.1.10","writecache_size":3,"fragment_cache_on_read":False,"fragment_cache_on_write":False,"config_params":{"dtl_mode":"no_sync","sco_size":4,"cluster_size":4,"write_buffer":128,"dtl_transport":"tcp"},"parallelism":{"proxies":1}}}
taskguid = ovscl.post('/storagerouters/{}/add_vpool/'.format(storagerouterguid), data=json.dumps(createpooldata))
ovscl.wait_for_task(taskguid, 60)
