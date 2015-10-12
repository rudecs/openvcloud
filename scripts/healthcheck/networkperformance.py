from JumpScale import j
import sys
import json
class OpennStorage():
    def __init__(self):
        self._localIp = None
        self._clusterIps = []
        self._internetSpeed = None
        # appened opverstorage to python path
        sys.path.append('/opt/OpenvStorage')
        j.logger.log('Installing iperf', 1)
        j.system.platform.ubuntu.install('iperf')
        
    
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
        j.system.process.executeAsync('iperf -s -D')
    
    def getbandwidthState(self, bandwidth):
        """
        Assuming 10Gbits network
        """
        bandwidth = float(bandwidth)
        if bandwidth < 50:
            return 'ERROR'
        elif bandwidth < 9000:
            return 'WARNING'
        return 'OK'
    
    def getClusterBandwidths(self):
        final = []
        for ip in self.clusterIps:
            result = {'category':'Bandwidth Test'}
            sshclient =  j.remote.cuisine.connect(ip, 22, 'rooter')
            j.logger.log('Installing iperf on %s' % ip, 1)
            sshclient.run('apt-get install iperf')
            tempfile = open('/tmp/tempfile.txt', 'w')
            output = sshclient.subprocess.call(['iperf', '--format', 'm', '-c', self.localIp ,'-r'], stdout=tempfile)
            tempfile.close()
            output = open('/tmp/tempfile.txt', 'r').read()
            tempfile.close()
            output = output.split(' ')
            bandwidth = output[-2]
            result['message'] = json.dumps({'IP':ip, 'bandwidth': ' '.join([bandwidth, 'Mbits/s'])})
            result['state'] = self.getbandwidthState(bandwidth)
            final.append(result)
        return final

def action(data):
    ovs = OpennStorage()
    ovs.runIperfServer()
    return ovs.getClusterBandwidths()

if __name__ == '__main__':
    action({})