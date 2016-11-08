from JumpScale import j
import libvirt


def main():
    ccl = j.clients.osis.getNamespace('cloudbroker')

    libvirt.virEventRegisterDefaultImpl()
    rocon = libvirt.openReadOnly()

    def callback(con, domain, event, detail, opaque):
        name = domain.name()
        print('State change for {}'.format(name))
        vm = next(iter(ccl.vmachine.search({'referenceId': domain.UUIDString()})[1:]), None)
        if vm:
            newstate = None
            if event == libvirt.VIR_DOMAIN_EVENT_STARTED:
                newstate = 'RUNNING'
            elif event == libvirt.VIR_DOMAIN_EVENT_STOPPED:
                newstate = 'HALTED'
            if newstate is not None:
                print('Updating state for vm {} to {}'.format(name, newstate))
                ccl.vmachine.updateSearch({'id': vm['id']}, {'$set': {'status': newstate}})

    rocon.domainEventRegisterAny(None, libvirt.VIR_DOMAIN_EVENT_ID_LIFECYCLE,
                                 callback, rocon)
    while True:
        libvirt.virEventRunDefaultImpl()


if __name__ == '__main__':
    main()
