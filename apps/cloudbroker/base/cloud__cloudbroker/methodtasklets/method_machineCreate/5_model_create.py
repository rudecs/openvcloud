def main(q, args, params, actor, tags, te):
    machine = actor.models.vmachine.new()
    machine.cloudspaceId = args['spaceId']
    machine.descr = args['description']
    machine.name = args['name']
    machine.nrCU = args['nrCU']
    params.result = actor.model_vmachine_set(machine.obj2dict())
    return params

