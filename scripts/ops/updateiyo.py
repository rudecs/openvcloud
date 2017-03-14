#!/usr/bin/env jspython
from JumpScale import j
import argparse


def update(clientid):
    cbmasteraio = j.atyourservice.get(name='cb_master_aio')
    ovciyo = j.atyourservice.get(name='ovc_itsyouonline')
    oauth = j.atyourservice.get(name='oauth_client', instance='itsyouonline')

    ovciyodict = cbmasteraio.hrd.getDict('dep.args.ovc_itsyouonline')
    ovciyodict['param.client_id'] = clientid
    cbmasteraio.hrd.set('dep.args.ovc_itsyouonline', ovciyodict)
    cbmasteraio.hrd.set('instance.param.itsyouonline.client_id', clientid)
    ovciyo.hrd.set('instance.param.client_id', clientid)
    oauth.hrd.set('instance.oauth.client.id', clientid)
    scopes = 'user:name,user:email'
    for group in ['admin', 'level1', 'level2', 'level3', 'ovs_admin', 'user']:
        scopes += ',user:memberof:{}.{}'.format(clientid, group)

    oauth.hrd.set('instance.oauth.client.scope', scopes)

    portal = j.atyourservice.get(name='portal')
    portal.restart()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clientid', required=True)
    options = parser.parse_args()
    update(options.clientid)
