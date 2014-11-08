#!/usr/bin/env python
from JumpScale import j


def main():
    import JumpScale.grid
    import JumpScale.portal
    from libcloud.compute.providers import get_driver
    from libcloud.compute.types import Provider
    pcl = j.core.portal.getClientByInstance('cloudbroker')
    ccl = j.core.osis.getClientForNamespace('cloudbroker')
    dummy = get_driver(Provider.DUMMY)(1)
    for size in dummy.list_sizes():
        if not ccl.size.search({'name': size.name})[1:]:
            cbsize = ccl.size.new()
            cbsize.name = size.name
            cbsize.description = size.name
            cbsize.disk = size.disk
            cbsize.memory = size.ram
            cbsize.vcpus = 1
            ccl.size.set(cbsize)

    # add dummy stack
    stack = ccl.stack.new()
    stack.id = 1
    stack.name = 'dev'
    stack.referenceId = "1"
    stack.type = "DUMMY"
    stack.status = "ENABLED"
    stack.gid = j.application.whoAmI.gid
    ccl.stack.set(stack)

    # add location
    loc = ccl.location.new()
    loc.gid = j.application.whoAmI.gid
    loc.name = 'Development'
    loc.locationCode = 'dev'
    loc.flag = 'black'
    ccl.location.set(loc)

    pcl.actors.libcloud.libvirt.registerNetworkIdRange(1, 200, 300)


if __name__ == '__main__':
    main()
