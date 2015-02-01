#!/usr/bin/env python
import netaddr
import sys
from JumpScale import j
from JumpScale.baselib.cmdutils import ArgumentParser

def migrate(network, gateway):
    import JumpScale.grid.osis
    allips = set(j.application.config.getDict('cloudscalers.networks.public_ip').values())
    whereami = j.application.config.get("cloudbroker.where.am.i")
    ccl = j.clients.osis.getForNamespace('cloudbroker')
    cloudspaces = ccl.cloudspace.simpleSearch({'location': whereami})
    usedpublicips = set()
    for space in cloudspaces:
        if space['status'] == 'DESTROYED':
            continue
        if '/' in space['publicipaddress']:
            ip = netaddr.IPNetwork(space['publicipaddress'])
            usedpublicips.add(str(ip.ip))
        else:
            usedpublicips.add(space['publicipaddress'])
    freeips = allips - usedpublicips
    pool = ccl.publicipv4pool.new()
    pool.id = str(network.cidr)
    pool.subnetmask = str(network.netmask)
    pool.gateway = str(gateway)
    pool.network = str(network.cidr.ip)
    import JumpScale.grid.osis
    freeipsinpool = set()
    for freeip in freeips:
        ip = netaddr.IPAddress(freeip)
        if ip in network:
            freeipsinpool.add(freeip)
    pool.pubips = list(freeipsinpool)
    ccl.publicipv4pool.set(pool)
    for spaced in cloudspaces:
        if spaced['status'] != 'DESTROYED':
            space = ccl.cloudspace.get(spaced['id'])
            space.status = 'DEPLOYED'
            if '/' not in space.publicipaddress and space.publicipaddress:
                space.publicipaddress = '%s/%s' % (space.publicipaddress, network.prefixlen)
            ccl.cloudspace.set(space)


if __name__ == '__main__':
    j.application.start('migrator')
    parser = ArgumentParser(description='Migrate Public IP addresses from hrd to osis')
    parser.add_argument('-n', '--network', required=True, help="Network including cidr eg. 10.101.190.0/24")
    parser.add_argument('-g', '--gateway', required=True, help="Gatewat of network")
    options = parser.parse_args()
    network = netaddr.IPNetwork(options.network)
    gateway = netaddr.IPAddress(options.gateway)
    if gateway not in network:
        print "Gateway is not in network"
        sys.exit(1)
    migrate(network, gateway)
    j.application.stop(0)
