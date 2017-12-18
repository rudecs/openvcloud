from JumpScale import j

descr = """
Upgrade script
* will update all Undefined IPs
* will patch apparmor

"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True


def action():
    from cloudbrokerlib.network import Network
    pcl = j.clients.portal.getByInstance('main')
    ccl = j.clients.osis.getNamespace('cloudbroker')
    machines = ccl.vmachine.search({'nics.ipAddress': 'Undefined', 'status': {'$nin':  ['ERROR', 'DESTROYED']}})[1:]
    network = Network(ccl)

    def getFreeIP(machine):
        cloudspace = ccl.cloudspace.get(machine['cloudspaceId'])
        return network.getFreeIPAddress(cloudspace)


    for machine in machines:
        with ccl.cloudspace.lock('{}_ip'.format(machine['cloudspaceId'])):
            j.console.info('Fetching machine details {}'.format(machine['name']))
            machinedata = pcl.actors.cloudapi.machines.get(machine['id'])
            if machinedata['status'] == 'RUNNING':
                for idx, interface in enumerate(machinedata['interfaces']):
                    if interface['ipAddress'] == 'Undefined':
                        machine['nics'][idx]['ipAddress'] = getFreeIP(machine)
                ccl.vmachine.set(machine)
            else:
                for nic in machine['nics']:
                    if nic['ipAddress'] == 'Undefined':
                        nic['ipAddress'] = getFreeIP(machine)
                ccl.vmachine.set(machine)
        j.console.info('Updating firewall')
        pcl.actors.cloudbroker.cloudspace.applyConfig(machine['cloudspaceId'])

    all_machines = ccl.vmachine.search({'status': {'$nin':  ['ERROR', 'DESTROYED']}}, size=0)[1:]
    used_ips = {}
    for machine in all_machines:
        cloudspace_id = machine['cloudspaceId']
        used_ips.setdefault(cloudspace_id, [])
        for nic in machine['nics']:
            if nic['ipAddress'] in used_ips[cloudspace_id]:
                raise RuntimeError("Duplicate ip found {name}".format(name=machine['name']))
            else:
                used_ips[cloudspace_id].append(nic['ipAddress'])



if __name__ == '__main__':
    print(action())
