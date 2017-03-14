#!/usr/bin/env jspython
from JumpScale import j
import argparse

def update(clientid, ovcsecret, ovssecret):
    j.system.fs.createDir('services/jumpscale__node.ssh__ovc_master/jumpscale__oauth_client__itsyouonline/')
    configure = j.atyourservice.get(name='ovc_configure_aio')
    configure.actions.prepare(configure)
    configure.actions.copyBack('ovc_master', 'jumpscale__oauth_client__itsyouonline')
    oauth = j.atyourservice.get(name='oauth_client', instance='itsyouonline')

    oauth.hrd.set('instance.oauth.client.id', clientid)
    scopes = 'user:name,user:email'
    for group in ['admin', 'level1', 'level2', 'level3', 'ovs_admin', 'user']:
        scopes += ',user:memberof:{}.{}'.format(clientid, group)
    oauth.hrd.set('instance.oauth.client.scope', scopes)
    if ovcsecret:
        oauth.hrd.set('instance.oauth.client.secret', ovcsecret)

    oauth.install(reinstall=True)
    portal = j.atyourservice.get(name='portal')
    portal.restart()

    for service in j.atyourservice.findServices(name='openvstorage_oauth'):
        service.hrd.set('instance.oauth.id', clientid)
        service.hrd.set('instance.oauth.secret', ovssecret)
        service.install(reinstall=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clientid', required=True)
    parser.add_argument('-s', '--ovcsecret', default=None)
    parser.add_argument('-o', '--ovssecret', default=None)
    options = parser.parse_args()
    update(options.clientid, options.ovcsecret, options.ovssecret)
