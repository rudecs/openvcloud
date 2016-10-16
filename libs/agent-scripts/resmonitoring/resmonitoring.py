from JumpScale import j
import capnp
from datetime import datetime
import json
import re

descr = """
Collects resources
"""

organization = "jumpscale"
author = "foudaa@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "resources.monitoring"
period = 60 * 60  # always in sec
timeout = period * 0.2
order = 1
enable = True
async = True
queue = 'process'
log = False
roles = ['controller']



def get_cached_accounts():
    cached_accounts = {}
    accl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "account")
    vmcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "vmachine")
    cscl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "cloudspace")
    accounts_ids = accl.search({'$query': {'status': {'$ne': 'DESTROYED'}}, '$fields': ['id']})[1:]
    for account_id in accounts_ids:
        cloudspaces_ids = cscl.search({'$query': {'accountId': account_id['id'], 'status': {'$ne': 'DESTROYED'}, 'gid': j.application.whoAmI.gid}, '$fields': ['id']})[1:]
        cached_accounts[account_id['id']] = {}
        for cloudspace_id in cloudspaces_ids:
            cached_accounts[account_id['id']][cloudspace_id['id']] = {}
            vms = vmcl.search({'$query': {'cloudspaceId': cloudspace_id['id'],
                                          'status': {'$ne': "DESTROYED"}},
                               '$fields': ['id', 'disks', 'sizeId', 'imageId', 'status', 'nics', 'stackId']})[1:]
            for vm in vms:
                cached_accounts[account_id['id']][cloudspace_id['id']][vm['id']] = {'id': vm['id'],
                                                                                    'disks': vm['disks'],
                                                                                    'sizeId': vm['sizeId'],
                                                                                    'status': vm['status'],
                                                                                    'nics': vm['nics'],
                                                                                    'imageId': vm['imageId'],
                                                                                    'stackId': vm['stackId']}

    return cached_accounts


def get_redis_instance(stackId, port='9999'):
    scl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "stack")
    stack = scl.search({'$query': {'id': stackId}})[1]
    url = stack['apiUrl']
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', url)
    if ip:
        redis = j.clients.redis.getRedisClient(ip[0], port)
    return redis, stack


def get_last_hour_val(redis, key):
    now = datetime.now()
    value = redis.get(key)
    if value:
        value = json.loads(value)

    if (now - datetime.utcfromtimestamp(float(value['h_last_epoch']))).total_seconds() / (60 * 60) < 2:
        return value['h_last']
    return 0

def action():
    now = datetime.now()
    month = now.month
    hour = now.hour
    day = now.day
    year = now.year
    capnp.remove_import_hook()
    cloudspace_capnp = capnp.load('../../CloudscalerLibcloud/CloudscalerLibcloud/schemas/space.capnp')
    # redis = j.clients.redis.getByInstance('system')

    imagecl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "image")
    sizescl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "size")
    dcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "disk")
    cscl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "cloudspace")
    vcl =  j.clients.osis.getNamespace('vfw')
    images_list = imagecl.search({'$fields': ['id', 'name']})[1:]
    sizes_list = sizescl.search({'$fields': ['id', 'memory']})[1:]
    sizes_dict = {}
    images_dict = {}
    for size in sizes_list:
        sizes_dict[size['id']] = size['memory']
    for image in images_list:
        images_dict[image['id']] = image['name']

    gid = j.application.whoAmI.gid
    # nid = j.application.whoAmI.nid
    cached_accounts = get_cached_accounts()

    for account_id, cloudspaces_dict in cached_accounts.items():
        folder_name = "/opt/var/active/resourcetracking/%s/%s/%s/%s/%s" % (account_id, year, month, day, hour)
        j.do.createDir(folder_name)

        for cloudspace_id, vms in cloudspaces_dict.items():
            cloudspace = cloudspace_capnp.CloudSpace.new_message()
            cloudspace.accountId = account_id
            cloudspace.cloudSpaceId = cloudspace_id
            cs = cscl.get(cloudspace_id)
            net = vcl.virtualfirewall.get("%s_%s" % (cs.gid, cs.networkId))
            nid = net.nid
            cloudspace.publicTX = get_last_hour_val(
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.pub-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            cloudspace.publicRX = get_last_hour_val(
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.pub-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            cloudspace.spaceRX = get_last_hour_val(
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.spc-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            cloudspace.spaceTX = get_last_hour_val(
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.spc-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))

            machines = cloudspace.init('machines', len(vms))
            for idx, (vm_id, machine_dict) in enumerate(vms.items()):
                iops_read = 0
                iops_write = 0
                disks_size = 0
                tx_value = 0
                rx_value = 0
                m = machines[idx]
                stack_id = machine_dict.get('stackId', None)
                # get Image name
                image_name = images_dict.get(machine_dict['imageId'], "")
                # get mem size
                memory_consumption = sizes_dict[machine_dict['sizeId']]
                # calculate disk size
                disks = dcl.search({'id': {'$in': machine_dict['disks']}})[1:]
                for disk in disks:
                    disks_size += disk['sizeMax']

                if machine_dict['status'] != "HALTED" and stack_id:
                    # get redis for this stack
                    redis, stack = get_redis_instance(stack_id)
                    nid = stack['referenceId']
                    # get CPU
                    cpu_key = 'stats:{gid}_{nid}:machine.CPU.utilisation@virt.{vm_id}'.format(gid=gid, nid=nid, vm_id=vm_id)
                    cpu_consumption = get_last_hour_val(redis, cpu_key)
                    # calculate iops
                    for disk_id in machine_dict['disks']:
                        disk_iops_read_key = "stats:{gid}_{nid}:disk.iops.read@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                        disk_iops_write_key = "stats:{gid}_{nid}:disk.iops.write@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                        iops_read += get_last_hour_val(redis, disk_iops_read_key)
                        iops_write += get_last_hour_val(redis, disk_iops_write_key)

                    # Calculate Network tx and rx
                    for nic in machine_dict['nics']:
                        mac = nic['macAddress']
                        tx_key = "stats:{gid}_{nid}:network.packets.tx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                        rx_key = "stats:{gid}_{nid}:network.packets.rx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                        tx_value += get_last_hour_val(redis, tx_key)
                        rx_value += get_last_hour_val(redis, rx_key)
                    # exec("m = machines[%s]" % idx)
                    m.iopsRead = iops_read
                    m.iopsWrite = iops_write
                    m.network.tx = tx_value
                    m.network.rx = rx_value
                    m.cpuSize = cpu_consumption

                else:
                    m.iopsRead = 0
                    m.iopsWrite = 0
                    m.network.tx = 0
                    m.network.rx = 0
                    m.cpuSize = 0
                m.imageName = image_name
                m.memSize = memory_consumption
                m.disksSize = disks_size
                m.status = machine_dict['status']
                # write files to disk
            with open("%s/%s.bin" % (folder_name, cloudspace_id), "w+b") as f:
                cloudspace.write(f)


if __name__ == '__main__':
    j.core.osis.client = j.clients.osis.getByInstance('main')
    rt = action()
