from JumpScale import j
import capnp
from datetime import datetime
import json
import urlparse

descr = """
Collects resources
"""

organization = "jumpscale"
author = "foudaa@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "resources.monitoring"
period = "0 * * * *"
timeout = 120
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


def get_redis_instance(stackId, stacks, port=9999):
    scl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "stack")
    if stackId not in stacks:
        stacks[stackId] = scl.get(stackId)
    ip = urlparse.urlparse(stacks[stackId].apiUrl).hostname
    redis = j.clients.redis.getRedisClient(ip, port)
    return redis, stacks[stackId]


def get_last_hour_val(redis, key, property='h_last'):
    now = datetime.now()
    value = redis.get(key)
    if value:
        value = json.loads(value)
        if value.get('h_last_epoch', 0):
            if (now - datetime.utcfromtimestamp(float(value['h_last_epoch']))).total_seconds() / (60 * 60) < 2:
                return value.get(property, 0)
    return 0


def get_node_redis(node, port=9999):
    for nicinfo in node.netaddr:
        if nicinfo['name'] == 'backplane1':
            ip = nicinfo['ip'][0]
            break
    else:
        return None
    redis = j.clients.redis.getRedisClient(ip, port)
    return redis


def action():
    import CloudscalerLibcloud
    import os
    stacks = {}

    now = datetime.now()
    month = now.month
    hour = now.hour
    day = now.day
    year = now.year
    capnp.remove_import_hook()
    schemapath = os.path.join(os.path.dirname(CloudscalerLibcloud.__file__), 'schemas', 'resourcemonitoring.capnp')
    cloudspace_capnp = capnp.load(schemapath)
    nodecl = j.clients.osis.getCategory(j.core.osis.client, 'system', 'node')
    imagecl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "image")
    sizescl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "size")
    dcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "disk")
    cscl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "cloudspace")
    vcl = j.clients.osis.getNamespace('vfw')
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
        folder_name = "/opt/jumpscale7/var/resourcetracking/active/%s/%s/%s/%s/%s" % (account_id, year, month, day, hour)
        j.do.createDir(folder_name)

        for cloudspace_id, vms in cloudspaces_dict.items():
            cloudspace = cloudspace_capnp.CloudSpace.new_message()
            cloudspace.accountId = account_id
            cloudspace.cloudSpaceId = cloudspace_id
            cs = cscl.get(cloudspace_id)
            net = vcl.virtualfirewall.get("%s_%s" % (cs.gid, cs.networkId))
            nid = net.nid
            node = nodecl.get("%s_%s" % (net.gid, net.nid))
            redis = get_node_redis(node)
            publicTX = get_last_hour_val(redis,
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.pub-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            publicRX = get_last_hour_val(redis,
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.pub-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            spaceRX = get_last_hour_val(redis,
                'stats:{gid}_{nid}:network.vfw.packets.rx@virt.spc-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))
            spaceTX = get_last_hour_val(redis,
                'stats:{gid}_{nid}:network.vfw.packets.tx@virt.spc-{id}'.format(gid=gid, nid=nid, id=hex(cs.networkId)))

            machines = cloudspace.init('machines', len(vms)+1)
            m = machines[0]
            m.type = 'routeros'
            nics = m.init('networks', 2)
            nic1 = nics[0]
            nic1.tx = publicTX
            nic1.tx = publicRX
            nic2 = nics[1]
            nic2.tx = spaceTX
            nic2.rx = spaceRX
            for idx, (vm_id, machine_dict) in enumerate(vms.items()):
                m = machines[idx + 1]
                m.type = 'vm'
                stack_id = machine_dict.get('stackId', None)
                # get Image name
                image_name = images_dict.get(machine_dict['imageId'], "")
                # get mem size
                memory_consumption = sizes_dict[machine_dict['sizeId']]
                # # calculate disk size
                # disks = dcl.search({'id': {'$in': machine_dict['disks']}})[1:]
                # for disk in disks:
                #     disks_size += disk['sizeMax']

                if machine_dict['status'] != "HALTED" and stack_id:
                    # get redis for this stack
                    redis, stack = get_redis_instance(stack_id, stacks)
                    nid = stack.referenceId
                    # get CPU
                    cpu_key = 'stats:{gid}_{nid}:machine.CPU.utilisation@virt.{vm_id}'.format(gid=gid, nid=nid, vm_id=vm_id)
                    cpu_seconds = get_last_hour_val(redis, cpu_key)
                    # calculate iops
                    disks_capnp = m.init('disks', len(machine_dict['disks']))
                    for index, disk_id in enumerate(machine_dict['disks']):
                        disk = dcl.get(disk_id)
                        disk_size = disk.sizeMax
                        disk_capnp = disks_capnp[index]
                        disk_capnp.size = disk_size
                        disk_iops_read_key = "stats:{gid}_{nid}:disk.iops.read@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                        disk_capnp.iopsRead = get_last_hour_val(redis, disk_iops_read_key)
                        disk_capnp.iopsReadMax = get_last_hour_val(redis, disk_iops_read_key, 'h_last_max')
                        disk_iops_write_key = "stats:{gid}_{nid}:disk.iops.write@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                        disk_capnp.iopsWrite = get_last_hour_val(redis, disk_iops_write_key)
                        disk_capnp.iopsWriteMax = get_last_hour_val(redis, disk_iops_write_key, 'h_last_max')

                    # Calculate Network tx and rx
                    nics = m.init("networks", len(machine_dict))
                    for index, nic in enumerate(machine_dict['nics']):
                        mac = nic['macAddress']
                        nic_capnp = nics[index]
                        tx_key = "stats:{gid}_{nid}:network.packets.tx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                        rx_key = "stats:{gid}_{nid}:network.packets.rx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                        nic_capnp.tx = get_last_hour_val(redis, tx_key)
                        nic_capnp.rx = get_last_hour_val(redis, rx_key)
                    m.cpuMinutes = cpu_seconds/60
                else:
                    m.cpuMinutes = 0
                m.imageName = image_name
                m.mem = memory_consumption
                m.status = machine_dict['status']
                # write files to disk
            with open("%s/%s.bin" % (folder_name, cloudspace_id), "w+b") as f:
                cloudspace.write(f)


if __name__ == '__main__':
    j.core.osis.client = j.clients.osis.getByInstance('main')
    rt = action()
