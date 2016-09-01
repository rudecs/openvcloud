from JumpScale import j
descr = """
This healthcheck calls the standard OpenVStorage healthcheck.  This can be found on : https://github.com/openvstorage/openvstorage-health-check

"""

organization = 'cloudscalers'
author = "foudaa@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['storagedriver']
period = 60 * 30 # 30min
timeout = 60 * 5
enable = False
async = True
queue = 'io'
log = True

LOG_TYPES = {0: 'ERROR',  #FAILURE
             1: 'OK',  #SUCCESS
             2: 'WARNING',
             3: 'OK',  #info
             4: 'ERROR',  #EXCEPTION
             5: 'SKIPPED',
             6: 'DEBUG'}



def action():
    import sys
    sys.path.insert(0, '/opt/OpenvStorage')
    from ovs.extensions.healthcheck.openvstorage.openvstoragecluster_health_check import OpenvStorageHealthCheck
    from ovs.extensions.healthcheck.arakoon.arakooncluster_health_check import ArakoonHealthCheck
    from ovs.extensions.healthcheck.alba.alba_health_check import AlbaHealthCheck
    roles = j.application.config.getList('grid.node.roles')

    alba = AlbaHealthCheck()
    alba.module = "Alba Module"
    arakoon = ArakoonHealthCheck()
    arakoon.module = "Arakoon Module"
    ovs = OpenvStorageHealthCheck()
    ovs.module = "OVS Module"

    def check_arakoon():
        """
        Checks all critical components of Arakoon
        """
        arakoon.checkArakoons()

    def check_openvstorage():
        """
        Checks all critical components of Open vStorage
        """
        ovs.getLocalSettings()
        ovs.checkOvsWorkers()
        ovs.checkOvsPackages()
        ovs.checkRequiredPorts()
        ovs.findZombieAndDeadProcesses()
        ovs.checkRequiredDirs()
        ovs.checkHypervisorManagementInformation()
        ovs.checkSizeOfLogFiles()
        ovs.checkIfDNSResolves()
        # ovs.checkModelConsistency()
        if 'cpunode' in roles:
            ovs.checkForHaltedVolumes()
            ovs.checkFileDriver()
            ovs.checkVolumeDriver()

    def check_alba():
        """
        Checks all critical components of Alba
        """
        alba.checkAlba()

    check_openvstorage()
    check_arakoon()
    check_alba()


if __name__ == '__main__':
    print action()
