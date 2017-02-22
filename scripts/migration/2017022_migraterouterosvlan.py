from JumpScale import j

vcl = j.clients.osis.getNamespace('vfw')
ccl = j.clients.osis.getNamespace('cloudbroker')
for vfw in vcl.virtualfirewall.search({})[1:]:
    space = next(iter(ccl.cloudspace.search({'gid': vfw['gid'], 'networkId': vfw['id']})[1:]), None)
    if space:
        externalnetwork = ccl.externalnetwork.get(space['externalnetworkId'])
        vfw['vlan'] = externalnetwork.vlan
        vcl.virtualfirewall.set(vfw)
