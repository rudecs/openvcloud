from JumpScale import j

scl = j.clients.osis.getNamespace('system')
ovs = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']
ovc = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))

def update():
    storage_drivers = ovc.get('/storagedrivers', params={'contents':'vdisks_guids,vpool,storagerouter'})['data']
    result = list()
    for sd in storage_drivers:
        result.append(dict(vpool=sd['mountpoint'].split('/')[-1], vpoolguid=sd['vpool_guid'], storagerouterguid=sd['storagerouter_guid'], diskcount=len(sd['vdisks_guids']), storageip=sd['storage_ip']))
    storage_routers = set()
    vpools = set()
    for r in result:
        storage_routers.add(r['storageip'])
        vpools.add(r['vpool'])
    max_vpool_name_length = max((len(vp) for vp in vpools))
    storage_routers = sorted(list(storage_routers))
    vpools = sorted(list(vpools))
    header = "{} | {} | totals".format("".ljust(max_vpool_name_length), " | ".join(storage_routers))
    print header
    for vpool in vpools:
        print "".ljust(len(header), '-')
        print "{} | {} | {}".format(vpool.ljust(max_vpool_name_length), " | ".join((str(next((r['diskcount'] for r in result if r['vpool'] == vpool and r['storageip'] == srip), '')).ljust(len(srip)) for srip in storage_routers)), sum((next((r['diskcount'] for r in result if r['vpool'] == vpool and r['storageip'] == srip), 0)) for srip in storage_routers))
    print "".ljust(len(header), '-')
    print "{} | {}".format('totals'.ljust(max_vpool_name_length), " | ".join((str(sum((next((r['diskcount'] for r in result if r['vpool'] == vp and r['storageip'] == srip), 0)) for vp in vpools)).ljust(len(srip)) for srip in storage_routers)))
update()