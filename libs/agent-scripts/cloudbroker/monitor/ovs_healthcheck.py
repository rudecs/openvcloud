from JumpScale import j
descr = """
check status of alertservice
"""

organization = 'cloudscalers'
author = "foudaa@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['storagenode']
period = 60 * 30 # 30min
timeout = 60 * 5
enable = True
async = True
queue = 'io'
log = False

LOG_TYPES = {0: 'ERROR',  #FAILURE
             1: 'OK',  #SUCCESS
             2: 'WARNINNG',
             3: 'OK',  #info
             4: 'ERROR',  #EXCEPTION
             5: 'SKIPPED',
             6: 'DEBUG'}


def logger(self, message, module, log_type, unattended_mode_name, unattended_print_mode=True):
    self.results.append({'message': message, 'category': module, 'state': LOG_TYPES[log_type]})

def action():
    import sys
    sys.path.insert(0, '/opt/OpenvStorage-healthcheck')
    sys.path.insert(0, '/opt/OpenvStorage')
    from utils.extension import Utils
    from openvstorage.openvstoragecluster_health_check import OpenvStorageHealthCheck
    from arakoon.arakooncluster_health_check import ArakoonHealthCheck
    from alba.alba_health_check import AlbaHealthCheck

    Utils.logger = logger
    utility = Utils(False, False)
    utility.results = []
    alba = AlbaHealthCheck(utility)
    alba.module = "Alba Module"
    arakoon = ArakoonHealthCheck(utility)
    arakoon.module = "Arakoon Module"
    ovs = OpenvStorageHealthCheck(utility)
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
        ovs.checkOvsProcesses()
        ovs.checkOvsWorkers()
        ovs.checkOvsPackages()
        ovs.checkRequiredPorts()
        ovs.findZombieAndDeadProcesses()
        ovs.checkRequiredDirs()
        ovs.checkHypervisorManagementInformation()
        ovs.checkSizeOfLogFiles()
        ovs.checkIfDNSResolves()
        ovs.checkModelConsistency()
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

    return utility.results


if __name__ == '__main__':
    print action()
