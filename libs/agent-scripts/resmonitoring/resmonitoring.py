from JumpScale import j
from datetime import datetime
import json

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


def groupby(items, key):
    result = {}
    for item in items:
        result.setdefault(item[key], []).append(item)
    return result


def get_cached_accounts():
    cached_accounts = {}
    accl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "account")
    vmcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "vmachine")
    dcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "disk")
    cscl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "cloudspace")

    def get_ids(obj):
        return obj['id']

    accounts_ids = map(get_ids, accl.search({'$query': {'status': {'$ne': 'DESTROYED'}}, '$fields': ['id']},
                                            size=0)[1:])
    cloudspaces = cscl.search({'$query': {'accountId': {'$in': accounts_ids},
                                          'status': {'$ne': 'DESTROYED'},
                                          'gid': j.application.whoAmI.gid},
                               '$fields': ['id', 'accountId', 'status', 'gid', 'networkId']}, size=0)[1:]
    vms = vmcl.search({'$query': {'cloudspaceId': {'$in': map(get_ids, cloudspaces)},
                                  'status': {'$ne': "DESTROYED"}},
                       '$fields': ['id', 'disks', 'sizeId', 'imageId', 'status', 'nics', 'stackId', 'cloudspaceId', 'memory', 'vcpus']},
                      size=0)[1:]
    diskids = []
    for vm in vms:
        diskids.extend(vm['disks'])
    disks = {disk['id']: disk for disk in dcl.search({'$query': {'id': {'$in': diskids}},
                                                      '$fields': ['id', 'sizeMax']},
                                                     size=0)[1:]}
    spacesperaccount = groupby(cloudspaces, 'accountId')
    vmsperspace = dict(groupby(vms, 'cloudspaceId'))
    for accountid, spaces in spacesperaccount.iteritems():
        for space in spaces:
            space = cached_accounts.setdefault(accountid, {}).setdefault(space['id'], space)
            space['vms'] = []
            for vm in vmsperspace.get(space['id'], []):
                vmdisks = []
                for diskid in vm['disks']:
                    disk = disks.get(diskid)
                    if disk:
                        vmdisks.append(disk)
                vm['disks'] = vmdisks
                space['vms'].append(vm)

    return cached_accounts


def get_last_hour_val(redis, key, property='h_last'):
    return get_val(redis, key).get(property, 0)


def get_val(redis, key):
    if redis is None:
        return {}
    now = datetime.utcnow()
    value = redis.get(key)
    if value:
        value = json.loads(value)
        if value.get('h_last_epoch', 0):
            if (now - datetime.utcfromtimestamp(float(value['h_last_epoch']))).total_seconds() / (60 * 60) < 2:
                return value
    return {}


def action():
    import CloudscalerLibcloud
    import os
    import capnp
    redises = {}

    now = datetime.utcnow()
    month = now.month
    hour = now.hour
    day = now.day
    year = now.year
    capnp.remove_import_hook()
    schemapath = os.path.join(os.path.dirname(CloudscalerLibcloud.__file__), 'schemas', 'resourcemonitoring.capnp')
    cloudspace_capnp = capnp.load(schemapath)
    nodecl = j.clients.osis.getCategory(j.core.osis.client, 'system', 'node')
    imagecl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "image")
    stackcl = j.clients.osis.getCategory(j.core.osis.client, "cloudbroker", "stack")
    vcl = j.clients.osis.getNamespace('vfw')
    virtualfirewalls = {vfw['id']: vfw for vfw in vcl.virtualfirewall.search({'gid': j.application.whoAmI.gid})[1:]}
    nodes = {node['id']: node for node in nodecl.search({'gid': j.application.whoAmI.gid})[1:]}
    stacks = {stack['id']: stack for stack in stackcl.search({'gid': j.application.whoAmI.gid})[1:]}
    images_list = imagecl.search({'$fields': ['id', 'name']})[1:]
    images_dict = {}
    for image in images_list:
        images_dict[image['id']] = image['name']

    gid = j.application.whoAmI.gid
    # nid = j.application.whoAmI.nid
    cached_accounts = get_cached_accounts()

    def get_node_redis(node, port=9999):
        redis = redises.get(node['id'])
        if redis is not None:
            for nicinfo in node['netaddr']:
                if nicinfo['name'] == 'backplane1':
                    ip = nicinfo['ip'][0]
                    break
            else:
                return None
            redis = j.clients.redis.getRedisClient(ip, port)
            redises[node['id']] = redis
        return redis

    for account_id, cloudspaces_dict in cached_accounts.items():
        folder_name = "/opt/jumpscale7/var/resourcetracking/active/%s/%s/%s/%s/%s" % \
                        (account_id, year, month, day, hour)
        j.do.createDir(folder_name)

        for cloudspace_id, cs in cloudspaces_dict.items():
            vms = cs['vms']
            cloudspace = cloudspace_capnp.CloudSpace.new_message()
            cloudspace.accountId = account_id
            cloudspace.cloudSpaceId = cloudspace_id
            if cs['status'] == 'DEPLOYED' and cs['networkId'] in virtualfirewalls:
                networkId = hex(cs['networkId'])
                net = virtualfirewalls[cs['networkId']]
                nid = net['nid']
                node = nodes[nid]
                redis = get_node_redis(node)
                data = dict(gid=gid, nid=nid, id=networkId)
                publicTX = get_last_hour_val(redis,
                                             'stats:{gid}_{nid}:network.vfw.packets.rx@virt.pub-{id}'.format(**data))
                publicRX = get_last_hour_val(redis,
                                             'stats:{gid}_{nid}:network.vfw.packets.tx@virt.pub-{id}'.format(**data))
                spaceRX = get_last_hour_val(redis,
                                            'stats:{gid}_{nid}:network.vfw.packets.rx@virt.spc-{id}'.format(**data))
                spaceTX = get_last_hour_val(redis,
                                            'stats:{gid}_{nid}:network.vfw.packets.tx@virt.spc-{id}'.format(**data))
            else:
                publicTX = publicRX = spaceRX = spaceTX = 0

            machines = cloudspace.init('machines', len(vms) + 1)
            m = machines[0]
            m.type = 'routeros'
            nics = m.init('networks', 2)
            nic1 = nics[0]
            nic1.tx = publicTX
            nic1.tx = publicRX
            nic1.type = 'external'
            nic2 = nics[1]
            nic2.tx = spaceTX
            nic2.rx = spaceRX
            nic2.type = 'space'

            for idx, machine_dict in enumerate(vms):
                vm_id = machine_dict['id']
                m = machines[idx + 1]
                m.type = 'vm'
                m.id = vm_id
                stack_id = machine_dict.get('stackId', None)
                # get Image name
                image_name = images_dict.get(machine_dict['imageId'], "")
                has_stack = machine_dict['status'] != "HALTED" and stack_id
                if has_stack:
                    # get redis for this stack
                    stack = stacks[stack_id]
                    nid = int(stack['referenceId'])
                    redis = get_node_redis(nodes[nid])
                    # get CPU
                    cpu_key = 'stats:{gid}_{nid}:machine.CPU.utilisation@virt.{vm_id}'.format(gid=gid, nid=nid, vm_id=vm_id)
                    cpu_seconds = get_last_hour_val(redis, cpu_key)
                    m.cpuMinutes = cpu_seconds / 60
                else:
                    redis = None
                    m.cpuMinutes = 0

                disks_capnp = m.init('disks', len(machine_dict['disks']))
                # calculate iops
                for index, disk in enumerate(machine_dict['disks']):
                    disk_id = disk['id']
                    disk_capnp = disks_capnp[index]
                    disk_capnp.id = disk_id
                    disk_capnp.size = disk['sizeMax']
                    disk_iops_read_key = "stats:{gid}_{nid}:disk.iops.read@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                    val = get_val(redis, disk_iops_read_key)
                    disk_capnp.iopsRead = val.get('h_last', 0)
                    disk_capnp.iopsReadMax = val.get('h_last_max', 0)
                    disk_iops_write_key = "stats:{gid}_{nid}:disk.iops.write@virt.{disk_id}" .format(gid=gid, nid=nid, disk_id=disk_id)
                    val = get_val(redis, disk_iops_write_key)
                    disk_capnp.iopsWrite = val.get('h_last', 0)
                    disk_capnp.iopsWriteMax = val.get('h_last_max', 0)

                # Calculate Network tx and rx
                nics = m.init("networks", len(machine_dict['nics']))
                for index, nic in enumerate(machine_dict['nics']):
                    mac = nic['macAddress']
                    nic_capnp = nics[index]
                    nic_capnp.type = 'external' if nic['type'] == 'PUBLIC' else 'space'
                    tx_key = "stats:{gid}_{nid}:network.packets.tx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                    rx_key = "stats:{gid}_{nid}:network.packets.rx@virt.{mac}".format(gid=gid, nid=nid, mac=mac)
                    nic_capnp.tx = get_last_hour_val(redis, tx_key)
                    nic_capnp.rx = get_last_hour_val(redis, rx_key)

                m.imageName = image_name
                m.mem = machine_dict['memory']
                m.vcpus = machine_dict['vcpus']
                m.status = machine_dict['status']
                # write files to disk
            with open("%s/%s.bin" % (folder_name, cloudspace_id), "w+b") as f:
                cloudspace.write(f)


if __name__ == '__main__':
    j.core.osis.client = j.clients.osis.getByInstance('main')
    rt = action()
