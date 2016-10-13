from JumpScale import j

scl = j.clients.osis.getNamespace('system')
ovs = scl.grid.get(j.application.whoAmI.gid).settings['ovs_credentials']
ovc = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))

def update():
    storage_drivers = ovc.get('/storagedrivers', params={'contents':'vdisks_guids,vpool,storagerouter'})['data']
    result = list()
    for sd in storage_drivers:
        result.append(dict(vpool=sd['mountpoint'].split('/')[-1], vpoolguid=sd['vpool_guid'], storagerouterguid=sd['storagerouter_guid'], diskcount=len(sd['vdisks_guids']), storageip=sd['storage_ip']))
	result.sort(key=lambda r: r['vpool'])
    for r in result:
        print r['vpool'], r['storageip'], r['diskcount']

update()