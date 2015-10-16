from JumpScale import j

j.application.start("pertests")

ssh_mgmtkey = ""


def singleLocalNodeTest(monitorIP, nasIP):

    j.tools.perftesttools.init(testname='vnas', monitorNodeIp=monitorIP, sshPort=22, redispasswd="", sshkey=ssh_mgmtkey)

    monitor = j.tools.perftesttools.getNodeMonitor()
    nas = j.tools.perftesttools.getNodeNAS(nasIP, 22, nrdisks=0, fstype="xfs", role='vnas', name="nas-frontend0")
    nas.createLoopDev('2000', '/storage/vnas/devloop-backend')
    host = j.tools.perftesttools.getNodeHost(nasIP, 22, name="host1")

    nas.initTest()
    nas.perftester.sequentialReadWrite(size="2000m", nrfiles=1)

if __name__ == '__main__':
    masterIP = ''
    nasIP = ''
    singleLocalNodeTest()
