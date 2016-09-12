from JumpScale import j
import JumpScale.grid.agentcontroller
import gevent
import time

class CleanerOVC():
    def __init__(self):
        self.adminuser = "admin"
        self.adminpass = "admin"

        print("[+] loading components")
        self.pcl = j.clients.portal.getByInstance('main')
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        self.scl = j.clients.osis.getNamespace('system')
        self.lcl = j.clients.osis.getNamespace('libvirt')
        self.acl = j.clients.agentcontroller.get()


    def cleanDatabase(self):
        print("[+] cleanning openvcloud model database")

        print("[+] cleanning cloudbroker model")
        self.ccl.vmachine.deleteSearch({})
        self.ccl.disk.deleteSearch({})
        self.ccl.cloudspace.deleteSearch({})
        self.ccl.account.deleteSearch({})
        self.scl.user.deleteSearch({})
        
        print("[+] cleanning libvirt model")
        self.lcl.image.deleteSearch({})
        
        print("[+] cleanning system model")
        self.scl.audit.deleteSearch({})
        self.scl.eco.deleteSearch({})
        self.scl.job.deleteSearch({})
        self.scl.log.deleteSearch({})
        self.scl.sessioncache.deleteSearch({})
        self.scl.nic.deleteSearch({})
        self.scl.machine.deleteSearch({})
        self.scl.disk.deleteSearch({})

        print("[+] creating new admin user")
        
        admin = '%s:%s' % (self.adminuser, self.adminpass)
        groups = 'admin,level1,level2,level3,finance,user,ovs_admin'
        email = 'lesley@racktivity.com'
        
        useradd = 'jsuser add -d %s:%s:%s:' % (admin, groups, email)
        j.do.execute(useradd, outputStdout=False)


    def _getImages(self):
        return self.ccl.image.search({'status': {'$ne': 'DESTROYED'}})

    def _removeImage(self, id):
        # set unavailable, then remove it
        self.pcl.actors.cloudbroker.image.updateNodes(id, [])
        self.pcl.actors.cloudbroker.image.delete(id)

    def cleanImages(self):
        items = self._getImages()
        length = items.pop(0)
        
        for x in items:
            if x['referenceId'] == '':
                self.ccl.image.delete(x['id'])

        items = self._getImages()
        length = items.pop(0)

        print("[+] removing: %d images" % length)
        jobs = [gevent.spawn(self._removeImage, x['referenceId']) for x in items]
        gevent.joinall(jobs)



    def _getVirtualMachines(self):
        return self.ccl.vmachine.search({'status': {'$ne': 'DESTROYED'}})
    
    def _removeVirtualMachine(self, id):
        self.pcl.actors.cloudbroker.machine.destroy(id, "cleaning environment")
    
    def cleanVirtualMachines(self):
        items = self._getVirtualMachines()
        length = items.pop(0)
        
        print("[+] removing: %d virtual machines" % length)
        jobs = [gevent.spawn(self._removeVirtualMachine, x['id']) for x in items]
        gevent.joinall(jobs)



    def _getCloudspaces(self):
        return self.ccl.cloudspace.search({'status': {'$ne': 'DESTROYED'}})
    
    def _removeCloudspace(self, aid, cid):
        self.pcl.actors.cloudbroker.cloudspace.destroy(aid, cid, "cleaning environment")
        
    def cleanCloudspaces(self):
        items = self._getCloudspaces()
        length = items.pop(0)
        
        print("[+] removing: %d cloudspaces" % length)
        jobs = [gevent.spawn(self._removeCloudspace, x['accountId'], x['id']) for x in items]
        gevent.joinall(jobs)



    def _getAccounts(self):
        return self.ccl.account.search({'status': {'$ne': 'DESTROYED'}})
    
    def _removeAccount(self, id):
        self.pcl.actors.cloudbroker.account.delete(id, "cleaning environment")
        
    def cleanAccounts(self):
        items = self._getAccounts()
        length = items.pop(0)
        
        print("[+] removing: %d accounts" % length)
        jobs = [gevent.spawn(self._removeAccount, x['id']) for x in items]
        gevent.joinall(jobs)



    def cleanStor(self):
        print("[+] removing the vmstor contents")

        command = "rm -rf /mnt/vmstor/*"

        self.acl.executeJumpscript(
            'jumpscale',
            'exec',
            role='storagedriver',
            gid=j.application.whoAmI.gid,
            args={'cmd': command}
        )



    def checking(self):
        print("[+] checking environment status")

        check = [
            self._getImages,
            self._getVirtualMachines,
            self._getCloudspaces,
            self._getAccounts
        ]
        
        for checker in check:
            x = checker()
            if x.pop(0) != 0:
                return False
        
        return True





cleaner = CleanerOVC()

if cleaner.checking():
    print("[-] warning: environment looks already clean !")

cleaner.cleanImages()
cleaner.cleanVirtualMachines()
cleaner.cleanCloudspaces()
cleaner.cleanAccounts()

print("[ ] waiting for pending tasks. If this become too long, hit Ctrl+C.")
while not cleaner.checking():
    time.sleep(1)

print("[+] everything looks clean from openvcloud side")
cleaner.cleanStor()
cleaner.cleanDatabase()

print("")
print("[+] environment reset, here are some tips now:")
print("[+] - you can login again using credentials: %s/%s" % (cleaner.adminuser, cleaner.adminpass))
print("[+] - images was cleared, you will need to deploy them again")
print("[+] - you probably need to clear you browser cache")
