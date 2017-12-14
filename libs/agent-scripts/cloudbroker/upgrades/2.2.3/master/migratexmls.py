from JumpScale import j

descr = """
Upgrade script
* will update all disks to have a proper order
* Add metadata iso disks

"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True


def action():
    from CloudscalerLibcloud.compute.drivers.libvirt_driver import OpenvStorageVolume, OpenvStorageISO, convertchar
    from CloudscalerLibcloud.utils.gridconfig import GridConfig
    from xml.etree import ElementTree

    def get_volume(disk):
        volumeclass = OpenvStorageVolume
        if disk['type'] == 'M':
            volumeclass = OpenvStorageISO
        driver = None
        volume = volumeclass(id=disk['referenceId'],
                             name=disk['name'], size=disk['sizeMax'],
                             driver=driver,
                             iotune=disk.get('iotune', {}),
                             )
        return volume


    def get_domain_disks(dom):
        if isinstance(dom, ElementTree.Element):
            xml = dom
        elif isinstance(dom, basestring):
            xml = ElementTree.fromstring(dom)
        disks = xml.findall('devices/disk')
        for disk in disks:
            if disk.attrib['device'] in ('disk', 'cdrom'):
                yield disk

    def get_disk_by_name(disks, name):
        for disk, volume in disks:
            if volume.name == name:
                return disk, volume

    ccl = j.clients.osis.getNamespace('cloudbroker')
    config = GridConfig()
    ovs_credentials = config.get('ovs_credentials')
    connection = {'ips': ovs_credentials['ips'],
                  'client_id': ovs_credentials['client_id'],
                  'client_secret': ovs_credentials['client_secret']}
    acl = j.clients.agentcontroller.get()


    def get_disk_guid(gid, name):
        devicename = '/{}.raw'.format(name)
        args = {'ovs_connection': connection, 'diskpath': devicename}
        job = acl.executeJumpscript('greenitglobe', 'lookup_disk_by_path', gid=gid, role='storagemaster', args=args)
        if job['state'] != 'OK':
            return False
        return job['result']

    lcl = j.clients.osis.getNamespace('libcloud')
    machines = ccl.vmachine.search({'status': {'$nin':  ['ERROR', 'DESTROYED']}}, size=0)[1:]
    for machine in machines:
        j.console.info('Updating machine {}'.format(machine['name']))
        xmlkey = 'domain_{}'.format(machine['referenceId'])
        if not lcl.libvirtdomain.exists(xmlkey):
            continue
        xml = lcl.libvirtdomain.get(xmlkey)
        xmldisks = list(get_domain_disks(xml))
        vmdisks = [(disk, get_volume(disk)) for disk in ccl.disk.search({'id': {'$in': machine['disks']}})[1:]]
        firstdisk, firstvolume = vmdisks[0]
        vmchanges = False
        for xmldisk in xmldisks:
            ismeta = xmldisk.attrib['device'] == 'cdrom'
            source = xmldisk.find('source')
            name = source.attrib['name']
            diskpair = get_disk_by_name(vmdisks, name)
            if not diskpair:
                if not ismeta:
                    # what is this?
                    continue

                diskguid = get_disk_guid(firstdisk['gid'], name)
                if diskguid is False:
                    continue

                vmchanges = True
                disk = ccl.disk.new()
                disk.name = 'Metadata iso'
                disk.type = 'M'
                disk.stackId = firstdisk['stackId']
                disk.accountId = firstdisk['accountId']
                disk.gid = firstdisk['gid']
                disk.referenceId = firstdisk['referenceId'].replace(firstvolume.vdiskguid, diskguid).replace(firstvolume.name, name)
                diskid = ccl.disk.set(disk)[0]
                machine['disks'].append(diskid)
            else:
                # lets fix the disk order
                target = xmldisk.find('target')
                dev = target.attrib['dev']
                disk, volume = diskpair
                disk['order'] = convertchar(dev[2:])
                ccl.disk.set(disk)
        for nic in machine['nics']:
            if nic.get('target') and not nic['deviceName']:
                nic['deviceName'] = nic['target']
                vmchanges = True

        if vmchanges:
            ccl.vmachine.set(machine)



if __name__ == '__main__':
    print(action())
