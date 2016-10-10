scl = j.clients.osis.getNamespace('system')
grid = scl.grid.get(j.application.whoAmI.gid)
ovscred = grid.settings['ovs_credentials']

ovscl = j.clients.openvstorage.get(ovscred['ips'], (ovscred['client_id'], ovscred['client_secret']))

pools = {pool['guid']: pool['name'] for pool in ovscl.get('/vpools', params={'contents': 'true'})['data']}


vmstorset = '''{"new_config_params":{"sco_size":4,"dtl_mode":"no_sync","dedupe_mode":"non_dedupe","write_buffer":128,"dtl_target":[],"cache_strategy":"none","readcache_limit":null}}'''
dataset = '''{"new_config_params":{"sco_size":32,"dtl_mode":"no_sync","dedupe_mode":"non_dedupe","write_buffer":256,"dtl_target":[],"cache_strategy":"none","readcache_limit":null}}'''
for disk in ovscl.get('/vdisks', params={'contents': 'vpool'})['data']:
    vpool = pools.get(disk['vpool_guid'])
    if vpool == 'vmstor':
        data = vmstorset
    else:
        data = dataset
    ovscl.post('/vdisks/{}/set_config_params'.format(disk['guid']), data=data)
