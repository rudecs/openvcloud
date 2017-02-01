from JumpScale import j
import json
libvirt = j.clients.osis.getNamespace('libvirt')
libcloud = j.clients.osis.getNamespace('libcloud')
cloudbroker = j.clients.osis.getNamespace('cloudbroker')
for location in cloudbroker.location.search({})[1:]:
    gid = location['gid']
    if not libvirt.networkids.exists(gid):
        j.console.info('Add networkids for {}'.format(gid))
        networkids = json.loads(libcloud.libvirtdomain.get('networkids_{}'.format(gid)))
        libvirt.networkids.set({'id': gid, 'networkids': networkids})
    else:
        j.console.info('Networkids for {} already exist'.format(gid))

