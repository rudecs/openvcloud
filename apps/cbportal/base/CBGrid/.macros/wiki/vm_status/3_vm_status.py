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

    cl=j.clients.redis.getGeventRedisClient("localhost", int(j.application.config.get('redis.port.redisp')))

    if cl.hexists("vmachines.status", id):
        vm = cl.hget("vmachines.status", id)
        vmachine = json.loads(vm)
    else:
        out = 'Could not find VMachine Object with id %s'  % id
        params.result = (out, args.doc)
        return params

    def objFetchManipulate(id):
        vmachine['epoch'] = j.base.time.epoch2HRDateTime(vmachine['epoch'])
        return vmachine

    push2doc = j.apps.system.contentmanager.extensions.macrohelper.push2doc

    return push2doc(args,params,objFetchManipulate)

def match(j, args, params, tags, tasklet):
    return True
