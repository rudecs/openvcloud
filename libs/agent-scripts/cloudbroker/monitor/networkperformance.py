from JumpScale import j
import sys
import json

organization = "0-complexity"
author = "hamdy.farag@codescalers.com"
order = 1
enable = True
async = True
log = True
queue = 'io'
interval = 30 * 600
roles = ['storage']
category = 'monitoring'

class OpenvStorage():
    def __init__(self):
        self._localIp = None
        self._clusterIps = []
        self._internetSpeed = None
        self._runingServer = None
        # appened opverstorage to python path
        sys.path.append('/opt/OpenvStorage')
        j.logger.log('Installing iperf', 1)
        j.system.platform.ubuntu.checkInstall('iperf', 'iperf')
        
    
    @property
    def localIp(self):
        if not self._localIp:
            self._localIp = j.system.net.getIpAddress('backplane1')[0][0]
        return self._localIp
            
    @property
    def clusterIps(self):
        if not self._clusterIps:
            from ovs.lib.storagerouter import StorageRouterList
            StorageRouterList.get_storagerouters()
            self._clusterIps = [router.ip for router in StorageRouterList.get_storagerouters() if\
                                router.ip != self.localIp]
        return self._clusterIps
    
    def runIperfServer(self):
        j.logger.log('Running iperf server', 1)
        self._runingServer = j.system.process.executeAsync('iperf', ['-s'])

    def stopIperfServer(self):
        if self._runingServer:
            self._runingServer.kill()
    
    def getbandwidthState(self, bandwidth):
        """
        Assuming 10Gbits network
        """
        bandwidth = bandwidth
        if bandwidth < 5000:
            return 'ERROR'
        elif bandwidth < 9000:
            return 'WARNING'
        return 'OK'
    
    def getClusterBandwidths(self):
        final = []
        for ip in self.clusterIps:
            result = {'category': 'Bandwidth Test'}
            sshclient = j.remote.cuisine.connect(ip, 22, 'rooter')
            j.logger.log('Installing iperf on %s' % ip, 1)
            if not sshclient.command_check('iperf'):
                sshclient.run('apt-get install iperf')
            output = sshclient.run('iperf -c %s --format m ' % self.localIp)
            output = output.split(' ')
            bandwidth = float(output[-2])
            result['message'] = json.dumps({'IP': ip, 'bandwidth': '%s %s' % (bandwidth, 'Mbits/s')})
            result['state'] = self.getbandwidthState(bandwidth)
            if result['state'] != 'OK':
                msg = "Bandwith between %s and %s is not sufficient reached %s" % (self.localIp, ip)
                print msg
                eco = j.errorconditionhandler.getErrorConditionObject(msg=msg, category='monitoring', level=1, type='OPERATIONS')
                eco.process()
            final.append(result)
        return final

def action():
    ovs = OpenvStorage()
    ovs.runIperfServer()
    results = ovs.getClusterBandwidths()
    ovs.stopIperfServer()
    return results

if __name__ == '__main__':
    action()