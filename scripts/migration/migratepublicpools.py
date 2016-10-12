from JumpScale import j
mcl = j.clients.mongodb.getByInstance('main')
ccl = j.clients.osis.getNamespace('cloudbroker')

for pool in mcl.cloudbroker.publicipv4pool.find({}):
    network = ccl.externalnetwork.new()
    network.name = 'Default network'
    network.network = pool['network']
    network.subnetmask = pool['subnetmask']
    network.gid = pool['gid']
    network.gateway = pool['gateway']
    network.ips = pool['pubips']
    networkid, _, _ = ccl.externalnetwork.set(network)
    for cloudspace in ccl.cloudspace.search({'gid': network.gid})[1:]:
        cloudspace['externalnetworkId'] = networkid
        cloudspace['externalnetworkip'] = cloudspace['publicipaddress']
        ccl.cloudspace.set(cloudspace)
