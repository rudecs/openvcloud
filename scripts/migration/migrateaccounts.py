from JumpScale import j
import multiprocessing
import time
import json
from collections import namedtuple
from xml.etree import ElementTree
from cloudbrokerlib import resourcestatus
import urlparse

IMAGEMAP = {
    'New Windows 2012r2 Standard': 'Windows 2012r2 Standard'
}

Job = namedtuple('Job', "process intervalcheck args kwargs")

class ProcessPool(object):
    def __init__(self, nworkers, interval=5):
        """
        Process Pool that executes n amount of workers defined by nworkers
        Interval is the sleeptime between the status updates
        """
        self.nworkers = nworkers
        # prepopulate worker jobs by amount of workers
        self.activejobs = [None] * self.nworkers
        self.queuedjobs = [] # list of jobs that are still queued
        self.finishedjobs = 0
        self.interval = interval

    def run(self):
        """
        Schedule and run all queued jobs
        """
        statcheck = 0
        j.console.messages([""] * min(self.nworkers + 1, len(self.queuedjobs) + 1))
        while self.queuedjobs or [x for x in self.activejobs if x]:
            # freeup workers for finished jobs
            for idx, job in enumerate(self.activejobs):
                if job and not job.process.is_alive():
                    if job.process.exitcode != 0:
                        print('Failed to migrate vm {}!!!'.format(job.args[0]))
                    self.activejobs[idx] = None
                    self.finishedjobs += 1
            if self.queuedjobs:
                # schedule queues jobs in workers
                emptyslots = []
                # find free slots
                for idx, job in enumerate(self.activejobs):
                    if job is None:
                        emptyslots.append(idx)

                # put work in free slots
                for emptyslot in emptyslots:
                    work = self.queuedjobs.pop(0)
                    process = multiprocessing.Process(target=work[0], args=work[2], kwargs=work[3])
                    process.start()
                    job = Job(process, *work[1:])
                    self.activejobs[emptyslot] = job
                    if not self.queuedjobs:
                        break

            # update status messages if needed
            remainingtime = (statcheck + self.interval) - time.time()
            queuedjobs = len(self.queuedjobs)
            runningjobs = len([x for x in self.activejobs if x])
            totaljobs = queuedjobs + runningjobs + self.finishedjobs
            refreshtime = int(self.interval if remainingtime < 0 else remainingtime)
            statusline = "Queued/Running/Finished/Total {}/{}/{}/{} Jobs ({}s)".format(queuedjobs, runningjobs, self.finishedjobs, totaljobs, refreshtime)
            if remainingtime < 0:
                messages = [statusline]
                for job in self.activejobs:
                    if job and job.intervalcheck:
                        messages.append(job.intervalcheck(*job.args, **job.kwargs))
                statcheck = time.time()
            else:
                messages[0] = statusline
            j.console.messages(messages, True)
            time.sleep(5)

    def add_job(self, func, intervalcheck, *args, **kwargs):
        """
        Add a job to the queue
        param func: function to execute takes *args and **kwargs
        param intervalcheck: function that should return a status line for this job takes *args and **kwargs
        param *args: Args passed to func and intervalcheck
        param *kwargs: kwargs passed to func and intervalcheck
        """
        self.queuedjobs.append((func, intervalcheck, args, kwargs))


# helper method for multiprocessing
def migrate_vm(vmid, newspace, debug=False, dryrun=False):
    migrator = Migrator(debug, dryrun)
    space = migrator.ccl.cloudspace.new()
    space.load(newspace)
    return migrator.migrate_vm(vmid, space)


class Migrator(object):
    def __init__(self, debug=False, dryrun=False, concurrency=1, cloudspaces=None, vms=None):
        self.acl = j.clients.agentcontroller.getByInstance('main')
        self.pcl = j.clients.portal.getByInstance('main')
        self.source_osis = j.clients.osis.getByInstance('source')
        self.osis = j.clients.osis.getByInstance('main')
        self.source_ccl = j.clients.osis.getNamespace('cloudbroker', self.source_osis)
        self.souce_scl = j.clients.osis.getNamespace('system', self.source_osis)
        self.source_vfw = j.clients.osis.getNamespace('vfw', self.source_osis)
        self.ccl = j.clients.osis.getNamespace('cloudbroker', self.osis)
        self.scl = j.clients.osis.getNamespace('system', self.osis)
        self._rgid = None
        ovs = self.scl.grid.get(self.rgid).settings['ovs_credentials']
        self.ovscl = j.clients.openvstorage.get(ovs['ips'], (ovs['client_id'], ovs['client_secret']))
        self.vfw = j.clients.osis.getNamespace('vfw', self.osis)
        self.lcl = j.clients.osis.getNamespace('libvirt', self.osis)
        self.cloudspaces = cloudspaces
        self.vms = vms
        self.concurrency = concurrency
        self.debug = debug
        self.dryrun = dryrun
        self.vmdiskguids = {}

    def info(self, msg, depth=0):
        if depth:
            print '  ' * depth,
        j.console.info(msg)

    @property
    def rgid(self):
        if self._rgid is None:
            self._rgid = self.ccl.location.search({})[1]['gid']
        return self._rgid

    def migrate_account(self, accountId):
        account = self.source_ccl.account.get(accountId)
        self.info('Migrating account {}'.format(account.name))
        # search if account already exists
        accounts = self.ccl.account.search({'name': account.name, 'status': {'$ne': 'DESTROYED'}})[1:]
        if not accounts:
            newaccount = self.empty(account, self.source_ccl.account.new)
            if not self.dryrun:
                newaccount.id, _, _ = self.ccl.account.set(newaccount)
        else:
            newaccount = self.ccl.account.get(accounts[0]['id'])
        for cloudspace in self.source_ccl.cloudspace.search({'accountId': accountId, 'status': 'DEPLOYED'})[1:]:
            if self.cloudspaces is not None and cloudspace['id'] not in self.cloudspaces:
                continue
            cloudspace = self.source_ccl.cloudspace.get(cloudspace['id'])
            self.migrate_space(cloudspace, newaccount)

    def empty(self, obj, newmethod):
        newobj = newmethod()
        newobj.load(obj.dump())
        newobj.id = None
        newobj.guid = None
        if self.debug:
            newobj.name += '_migrated'
        return newobj

    def get_vms(self, cs_id):
        all_vms = self.source_ccl.vmachine.search({
            'status': {'$nin': resourcestatus.Machine.INVALID_STATES},
            'cloudspaceId': cs_id
        })[1:]
        def vmfilter(vm):
            if self.vms and vm['id'] not in self.vms:
                return False
            return self.source_ccl.disk.count({'id': {'$in': vm['disks']}, 'type': 'P'}) == 0

        vms = filter(vmfilter, all_vms)
        return vms

    def migrate_space(self, cloudspace, newaccount):
        self.info('Migrating space {}'.format(cloudspace.name), 1)
        cloudspacedata = cloudspace.dump()
        vfwdata = self.source_vfw.virtualfirewall.searchOne({'id': cloudspacedata['networkId']})
        sourceip = self.get_source_ip(vfwdata['nid'])
        newcloudspaceId = self.pcl.actors.cloudbroker.cloudspace.migrateCloudspace(newaccount.id, cloudspacedata, vfwdata, sourceip, self.rgid)
        newcloudspace = self.ccl.cloudspace.searchOne({'id': newcloudspaceId})
        vms = self.get_vms(cloudspace.id)
        if self.concurrency > 1:
            pool = ProcessPool(self.concurrency, interval=60)
            for vm in vms:
                pool.add_job(migrate_vm, self.vm_status, vm['id'], newcloudspace, self.debug, self.dryrun)
            pool.run()
        else:
            for vm in vms:
                self.info('Migrating vm-{}: {}'.format(vm['id'], vm['name']), 2)
                migrate_vm(vm['id'], newcloudspace, self.debug, self.dryrun)

        cloudspace.status = 'DESTROYED'
        if not self.dryrun:
            self.source_ccl.cloudspace.set(cloudspace)

    def vm_status(self, vmid, cloudspace, *args):
        try:
            if vmid not in self.vmdiskguids:
                oldvm = self.source_ccl.vmachine.get(vmid)
                newvm = self.ccl.vmachine.searchOne({
                    'name': oldvm.name,
                    'status': {'$in': ['MIGRATING', 'HALTED', 'PAUSED', 'RUNNING']},
                    'cloudspaceId': cloudspace['id']
                })
                if not newvm:
                    return "VM {} is being prepared for migration".format(vmid)
                if newvm['status'] == 'RUNNING':
                    return "VM {} finished migration".format(vmid)
                vmdisks = self.ccl.disk.search({'id': {'$in': newvm['disks']}})[1:]
                vmdiskguids = [disk['referenceId'].split('@')[-1] for disk in vmdisks if disk['referenceId']]
                if not vmdiskguids:
                    return "VM {} is being prepared for migration".format(vmid)
                self.vmdiskguids[vmid] = vmdiskguids
            vmdiskguids = self.vmdiskguids[vmid]
            items = []
            for vmdiskguid in vmdiskguids:
                items.append(('guid', 'EQUALS', vmdiskguid))
            query = json.dumps({'type': 'OR', 'items': items})
            params = {'contents': 'name,size,info', 'query': query}
            data = self.ovscl.get('/vdisks', params=params)
            totalsize = 0.
            usedsize = 0.
            for disk in data['data']:
                totalsize += disk['size']
                usedsize += disk['info']['stored']
            return "VM {} is being migrated disk at {:.2f}%".format(vmid, (usedsize/totalsize) * 100)
        except Exception as e:
            return "Failed get status of migration for VM {}: {}".format(vmid, e)

    def get_source_ip(self, nid):
        node = self.souce_scl.node.get(nid)
        for net in node.netaddr:
            if net['name'] == 'backplane1':
                return net['ip'][0]

    def transform_xml(self, sourcexml, newxml):
        srcdom = ElementTree.fromstring(sourcexml)
        newdom = ElementTree.fromstring(newxml)
        newdisks = {}
        newnics = {}
        for disk in newdom.findall('devices/disk'):
            target = disk.find('target')
            newdisks[target.attrib['dev']] = disk
        for nic in newdom.findall('devices/interface'):
            mac = nic.find('mac')
            newnics[mac.attrib['address']] = nic

        for disk in srcdom.findall('devices/disk'):
            target = disk.find('target')
            newdisk = newdisks[target.attrib['dev']]
            source = disk.find('source')
            newsource = newdisk.find('source')
            source.attrib['name'] = newsource.attrib['name']
            sourcehost = source.find('host')
            newhost = newsource.find('host')
            if 'username' in source.attrib:
                # if source has username/password this means source is OVS EE lets just overwirte username password
                if 'username' in newsource:
                    source.attrib['username'] = newsource.attrib['username']
                    source.attrib['passwd'] = newsource.attrib['passwd']
                else:
                    source.attrib.pop('username')
                    source.attrib.pop('passwd')
            else:
                # check if destination has password if so we need to insert username password in hakish way
                if 'username' in newsource.attrib:
                    source.attrib['name'] += ":username={username}:password={passwd}".format(**newsource.attrib)
            sourcehost.attrib['name'] = newhost.attrib['name']
            sourcehost.attrib['port'] = newhost.attrib['port']
            sourcehost.attrib['transport'] = newhost.attrib['transport']

        for nic in srcdom.findall('devices/interface'):
            mac = nic.find('mac').attrib['address']
            newnic = newnics[mac]
            target = nic.find('target')
            newtarget = newnic.find('target')
            target.attrib['dev'] = newtarget.attrib['dev']
            source = nic.find('source')
            newsource = newnic.find('source')
            source.attrib['network'] = newsource.attrib['network']
        seclabel = srcdom.find('seclabel')
        if seclabel is not None:
            srcdom.remove(seclabel)

        return ElementTree.tostring(srcdom)


    def migrate_vm(self, vmid, newspace):
        import libvirt
        vm = self.source_ccl.vmachine.get(vmid)
        vmdata = vm.dump()
        # update imageid
        oldimage = self.source_ccl.image.get(vm.imageId)
        imagename = IMAGEMAP.get(oldimage.name, oldimage.name)
        vmdata['imagename'] = imagename
        oldsize = self.source_ccl.size.get(vm.sizeId)
        vmdata['memory'] = oldsize.memory
        vmdata['vcpus'] = oldsize.vcpus
        vmdata['networkId'] = newspace.networkId
        vmdata['disks'] = []
        for diskid in vm.disks:
            disk = self.source_ccl.disk.get(diskid)
            vmdata['disks'].append(disk.dump())
        if self.dryrun:
            data = {'xml': 'xml', 'stackId': self.ccl.stack.list()[0], 'id': self.ccl.vmachine.list()[0]}
        else:
            data = self.pcl.actors.cloudbroker.machine.prepareForMigration(newspace.id, vmdata)
        newvm = self.ccl.vmachine.get(data['id'])
        targetStack = self.ccl.stack.get(data['stackId'])

        # now we migrate
        sourcestack = self.source_ccl.stack.get(vm.stackId)
        sourcecon = libvirt.open(sourcestack.apiUrl)
        try:
            domain = sourcecon.lookupByUUIDString(vm.referenceId)
        except:
            domain = None
        if domain and domain.info()[0] == libvirt.VIR_DOMAIN_RUNNING:
            # create network
            destcon = libvirt.open(targetStack.apiUrl)
            xml = domain.XMLDesc(libvirt.VIR_DOMAIN_XML_MIGRATABLE)
            newxml = self.transform_xml(xml, data['xml'])
            flags = libvirt.VIR_MIGRATE_COMPRESSED | libvirt.VIR_MIGRATE_LIVE | libvirt.VIR_MIGRATE_NON_SHARED_DISK | \
                    libvirt.VIR_MIGRATE_UNDEFINE_SOURCE | libvirt.VIR_MIGRATE_PEER2PEER
            uri = 'tcp://{}'.format(urlparse.urlparse(targetStack.apiUrl).hostname)
            if not self.dryrun:
                domain.migrate2(destcon, flags=flags, dxml=newxml, dname='vm-{}'.format(newvm.id), uri=uri)
        else:
            # we copy over the data
            # not supported just yet!!!
            raise RuntimeError("We do not support migrating vms that are not running!")
            qemujobs = []
            for sourcedisk, disk in disks:
                sourceurl = sourcedisk.referenceId.split('@')[0].replace('://', ':')
                desturl = disk.referenceId.split('@')[0].replace('://', ':')
                self.info('Copying disk {} to {}'.format(sourceurl, desturl), 3)
                self.qemu_img(['info', sourceurl], True)
                convertcmd = ['convert', '-n', '-p', '-O', 'raw', '-f', 'raw', sourceurl, desturl]
                if not self.dryrun:
                    qemujobs.append(self.qemu_img(convertcmd, sync=False))
            for qemujob in qemujobs:
                qemujob.wait()

        if not self.dryrun:
            update = {'status': 'DELETED', 'deletionTime': int(time.time())}
            self.source_ccl.vmachine.updateSearch({'id': vm.id}, {'$set': update})
            self.source_ccl.disk.updateSearch({'id': {'$in': vm.disks}}, {'$set': {'status': 'DELETED'}})
            self.ccl.vmachine.updateSearch({'id': newvm.id}, {'$set': {'status': 'RUNNING'}})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--accounts', help='Comma seperated accountids that require migration', required=True)
    parser.add_argument('-c', '--cloudspaces', dest='cloudspaces', default=None, help='Filter for cloudspaces to migrate')
    parser.add_argument('-m', '--vm', dest='vms', default=None, help='Filter for vms to migrate')
    parser.add_argument('-d', '--dry-run', dest='dry', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('-n', '--concurrency', dest='concurrency', type=int, default=1, help='Amount of VMs to migrate at once')
    parser.add_argument('-s', '--status', dest='status', default=False, action='store_true', help='Show status for vm')
    options = parser.parse_args()
    cloudspaces = None
    vms = None
    if options.cloudspaces:
        cloudspaces = [int(cs) for cs in options.cloudspaces.split(',')]
    if options.vms:
        vms = [int(vm) for vm in options.vms.split(',')]
    migrator = Migrator(options.debug, options.dry, options.concurrency, cloudspaces, vms)
    if not options.status:
        for accountid in options.accounts.split(','):
            migrator.migrate_account(int(accountid))
    else:
        cloudspace = migrator.ccl.cloudspace.searchOne({'id': cloudspaces[0]})
        while True:
            msg = migrator.vm_status(vms[0], cloudspace)
            print msg
            if 'finished' in msg:
                break
            time.sleep(60)

