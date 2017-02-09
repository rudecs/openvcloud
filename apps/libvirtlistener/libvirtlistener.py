from JumpScale import j
import libvirt


def main():
    ccl = j.clients.osis.getNamespace('cloudbroker')

    libvirt.virEventRegisterDefaultImpl()
    rocon = libvirt.open()

    def callback(con, domain, event, detail, opaque):
        name = domain.name()
        print('State change for {}'.format(name))
        vm = next(iter(ccl.vmachine.search({'referenceId': domain.UUIDString()})[1:]), None)
        if vm:
            try:
                domainstate, reason = domain.state()
                name = domain.name()
            except libvirt.libvirtError:
                # vm was removed
                return
            if domainstate == libvirt.VIR_DOMAIN_SHUTOFF and reason == libvirt.VIR_DOMAIN_SHUTOFF_CRASHED:
                tags = ''
                msg = ''
                if name.startswith('vm-'):
                    machineId = int(domain.name().split('-')[-1])
                    msg = "VM {} has crashed".format(machineId)
                    vm = ccl.vmachine.get(machineId)
                    cloudspace = ccl.cloudspace.get(vm.cloudspaceId)
                    tags = 'machineId:{} cloudspaceId:{} accountId:{}'.format(machineId, cloudspace.id, cloudspace.accountId)
                elif name.startswith('routeros_'):
                    networkid = int(name.split('_')[-1], 16)
                    cloudspaces = ccl.cloudspace.search({'networkId': networkid})[1:]
                    if not cloudspaces:
                        return  # orphan vm we dont care
                    tags = 'cloudspaceId:{}'.format(cloudspaces[0]['id'])

                print('VM crashed, starting it again')
                domain.create()
                j.errorconditionhandler.raiseOperationalWarning(msg, 'selfhealing', tags=tags)
                return
            newstate = None
            if event == libvirt.VIR_DOMAIN_EVENT_STARTED:
                newstate = 'RUNNING'
            elif event == libvirt.VIR_DOMAIN_EVENT_STOPPED:
                newstate = 'HALTED'
            if newstate is not None:
                print('Updating state for vm {} to {}'.format(name, newstate))
                # update the state if its not destroyed already
                ccl.vmachine.updateSearch({'id': vm['id'], 'status': {'$ne': 'DESTROYED'}}, {'$set': {'status': newstate}})

    rocon.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                 callback, rocon)
    while True:
        libvirt.virEventRunDefaultImpl()


if __name__ == '__main__':
    main()
