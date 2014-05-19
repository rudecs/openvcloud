import datetime
import JumpScale.grid.osis

def main(j, args, params, tags, tasklet):
    id = args.getTag('id')
    if not id:
        out = 'Missing VMachine ID param "id"'
        params.result = (out, args.doc)
        return params

    osiscl = j.core.osis.getClient(user='root')
    cbosis = j.core.osis.getClientForNamespace('cloudbroker', osiscl)
    try:
        obj = cbosis.vmachine.get(id)
    except:
        out = 'Could not find VMachine Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    def objFetchManipulate(id):
        data = dict()
        size = cbosis.size.get(obj.sizeId)
        stack = cbosis.stack.get(obj.stackId)
        image = cbosis.image.get(obj.imageId)
        space = cbosis.cloudspace.get(obj.cloudspaceId)
        fields = ('name', 'id', 'descr', 'imageId', 'stackId', 'status', 'hostName', 'hypervisorType', 'cloudspaceId')
        for field in fields:
            data[field.lower()] = getattr(obj, field, 'N/A')

        data['nics'] = '||Name||MAC Address||IP Address||\n'
        for nic in obj.nics:
            data['nics'] += '|%s|%s|%s|\n' % (nic.deviceName or 'N/A', nic.macAddress or 'N/A', nic.ipAddress or 'N/A')

        data['disks'] = '||Path||Order||Space||\n'
        for diskid in obj.disks:
            disk = cbosis.disk.get(diskid)
            data['disks'] += '|%s|%s|%s|\n' % (disk.diskPath or 'N/A', disk.order or 'N/A', '%s GB used of %s GB' % (disk.sizeUsed, disk.sizeMax))

        data['createdat'] = j.base.time.epoch2HRDateTime(obj.creationTime)
        data['size'] = '%s vCPUs, %s Memory, %s' % (size.vcpus, size.memory, size.description)
        data['image'] = image.name
        data['stackname'] = stack.name
        data['spacename'] = space.name
        return data

    push2doc = j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True