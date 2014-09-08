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
    osiscl = j.core.osis.getClient(user='root')
    cbosis = j.core.osis.getClientForNamespace('cloudbroker', osiscl)
    try:
        obj = cbosis.vmachine.get(id)
    except:
        out = 'Could not find VMachine Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    cl=j.clients.redis.getGeventRedisClient("localhost", int(j.application.config.get('redis.port.redisp')))

    stats = dict()
    if cl.hexists("vmachines.status", id):
        vm = cl.hget("vmachines.status", id)
        stats = json.loads(vm)

    def objFetchManipulate(id):
        data = dict()
        try:
            size = cbosis.size.get(obj.sizeId).dump()
        except Exception:
            size = {'vcpus': 'N/A', 'memory': 'N/A', 'description':'N/A'}
        try:
            stack = cbosis.stack.get(obj.stackId).dump()
        except Exception:
            stack = {'name': 'N/A', 'referenceId': 'N/A'}
        try: 
            image = cbosis.image.get(obj.imageId).dump()
        except Exception:
            image = {'name':'N/A'}
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

        fields = ('name', 'id', 'descr', 'imageId', 'stackId', 'status', 'hostName', 'hypervisorType', 'cloudspaceId')
        for field in fields:
            data[field.lower()] = getattr(obj, field, 'N/A')

        nwinfo = dict()
        try:
            libvirtclient = j.core.osis.getClientForNamespace('libvirt', osiscl)
            nwinfo = libvirtclient.node.get(str(obj.referenceId)).dump()
            data['nics'] = '||Name||MAC Address||IP Address||\n'

            for nic in obj.nics:
                data['nics'] += '|%s|%s|%s|\n' % (nic.deviceName or 'N/A', nwinfo.get('macaddress', 'N/A') or 'N/A', nic.ipAddress or 'N/A')
        except Exception:
            data['nics'] = 'NIC information is not available'

        data['disks'] = '||Path||Order||Space||\n'
        if hasattr(obj, 'disks'):
            for diskid in obj.disks:
                try:
                    disk = cbosis.disk.get(diskid)
                    data['disks'] += '|%s|%s|%s|\n' % (disk.diskPath or 'N/A', disk.order or 'N/A', '%s GB used of %s GB' % (disk.sizeUsed, disk.sizeMax))
                except Exception:
                    data = {'disks': 'Disks info is not available'}

        if hasattr(obj, 'creationTime'):
            data['createdat'] = j.base.time.epoch2HRDateTime(obj.creationTime)
        if hasattr(obj, 'deletionTime'):
            data['deletedat'] = j.base.time.epoch2HRDateTime(obj.deletionTime) if obj.deletionTime else 'N/A'
        data['size'] = '%s vCPUs, %s Memory, %s' % (size['vcpus'], size['memory'], size['description'])
        data['image'] = image['name']
        data['stackname'] = stack['name']
        data['spacename'] = space['name']
        data['stackrefid'] = stack['referenceId'] or 'N/A'

        for k, v in stats.iteritems():
            if k == 'epoch':
                v = j.base.time.epoch2HRDateTime(stats['epoch'])
            if k == 'disk_size':
                size, unit = j.tools.units.bytes.converToBestUnit(stats['disk_size'], 'K')
                v = '%.2f %siB' % (size, unit)
            data['stats_%s' % k] = v

        return data

    push2doc = j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
