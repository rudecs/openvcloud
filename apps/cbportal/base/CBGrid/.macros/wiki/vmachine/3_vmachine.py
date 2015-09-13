import datetime
import JumpScale.grid.osis
import JumpScale.baselib.units
try:
    import ujson as json
except Exception:
    import json

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing VMachine ID param "id"'
        params.result = (out, args.doc)
        return params

    id = int(id)
    osiscl = j.clients.osis.getByInstance('main')
    cbosis = j.clients.osis.getNamespace('cloudbroker', osiscl)
    try:
        obj = cbosis.vmachine.get(id)
    except:
        out = 'Could not find VMachine Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    try:
        cl = j.clients.redis.getByInstance('system')
    except:
        cl = None

    stats = dict()
    if cl and cl.hexists("vmachines.status", id):
        vm = cl.hget("vmachines.status", id)
        stats = json.loads(vm)

    data = {'stats_image': 'N/A', 'stats_parent_image': 'N/A', 'stats_disk_size': '-1',
            'stats_state': 'N/A', 'stats_ping': 'N/A', 'stats_hdtest': 'N/A', 'stats_epoch': 'N/A'}
    try:
        size = cbosis.size.get(obj.sizeId).dump()
    except Exception:
        size = {'vcpus': 'N/A', 'memory': 'N/A', 'description':'N/A'}
    try:
        stack = cbosis.stack.get(obj.stackId).dump()
    except Exception:
        stack = {'name': 'N/A', 'referenceId': 'N/A', 'type': 'UNKNOWN'}
    try: 
        image = cbosis.image.get(obj.imageId).dump()
        ccl = j.clients.osis.getNamespace('libvirt')
        imagedata = ccl.image.search({'name': image['name']})[1:]
        imageid = imagedata[0]['id'] if imagedata else None
    except Exception:
        image = {'name':'N/A'}
        imageid = None
    try:
        space = cbosis.cloudspace.get(obj.cloudspaceId).dump()
        data['accountId'] = space['accountId']
    except Exception:
        data['accountId'] = 0
        space = {'name': 'N/A'}
    data['accountName'] = 'N/A'
    if data['accountId']:
        try:
            account = cbosis.account.get(space['accountId']).dump()
            data['accountName'] = account['name']
        except:
            pass

    fields = ('name', 'id', 'descr', 'imageId', 'stackId', 'status', 'hostName', 'hypervisorType', 'cloudspaceId', 'tags')
    for field in fields:
        data[field] = getattr(obj, field, 'N/A')

    nwinfo = dict()
    try:
        libvirtclient = j.clients.osis.getNamespace('libvirt', osiscl)
        nwinfo = libvirtclient.node.get(str(obj.referenceId)).dump()
        data['nics'] = '||Name||MAC Address||IP Address||\n'

        for nic in obj.nics:
            data['nics'] += '|%s|%s|%s|\n' % (nic.deviceName or 'N/A', nwinfo.get('macaddress', 'N/A') or 'N/A', nic.ipAddress or 'N/A')
    except Exception:
        data['nics'] = 'NIC information is not available'

    data['disks'] = cbosis.disk.search({'id': {'$in': obj.disks}})[1:]
    diskstats = stats.get('diskinfo', [])
    disktypemap = {'D': 'Data', 'B': 'Boot', 'T': 'Temp'}
    for disk in data['disks']:
        disk['type'] = disktypemap.get(disk['type'], disk['type'])
        for diskinfo in diskstats:
            if disk['referenceId'].endswith(diskinfo['devicename']):
                disk.update(diskinfo)
                disk['footprint'] = '%.2f' % j.tools.units.bytes.toSize(disk['footprint'], output='G')
                break

    if hasattr(obj, 'creationTime'):
        data['createdat'] = j.base.time.epoch2HRDateTime(obj.creationTime)
    if hasattr(obj, 'deletionTime'):
        data['deletedat'] = j.base.time.epoch2HRDateTime(obj.deletionTime) if obj.deletionTime else 'N/A'
    data['size'] = '%s vCPUs, %s Memory, %s' % (size['vcpus'], size['memory'], size['description'])
    data['image'] = '[%s|image?id=%s]' % (image['name'], imageid) if imageid else image['name']
    data['stackname'] = stack['name']
    data['spacename'] = space['name']
    data['stackrefid'] = stack['referenceId'] or 'N/A'
    data['hypervisortype'] = stack['type']

    for k, v in stats.iteritems():
        if k == 'epoch':
            v = j.base.time.epoch2HRDateTime(stats['epoch'])
        if k == 'disk_size':
            if isinstance(stats['disk_size'], basestring):
                v = stats['disk_size']
            else:
                size, unit = j.tools.units.bytes.converToBestUnit(stats['disk_size'], 'K')
                v = '%.2f %siB' % (size, unit)
        data['stats_%s' % k] = v

    args.doc.applyTemplate(data)
    params.result = (args.doc, args.doc)
    return params

def match(j, args, params, tags, tasklet):
    return True
