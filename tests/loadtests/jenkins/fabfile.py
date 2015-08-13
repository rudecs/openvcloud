import sys
import requests
import uuid
# import pxssh
import time
import commands
import csv
from operator import add
import os
# import pexpect
from os.path import expanduser
import subprocess
from fabric.api import env, run, sudo, cd, settings


URL = 'http://cpu01.lenoir1.vscalers.com/'
USERNAME = 'loadtester'
PASSWORD = 'rooterR00t3r'
CLOUD_SPACE_ID = 91
UBUNNTU_SIZE_IDS = [2]
WINDOWS_SIZE_IDS = [4]
UBUNTU_IMAGE_ID = 2
WINDOWS_IMAGE_ID = 4
WINDOWS_DISK_SIZE = 16
UBUNTU_DISK_SIZE = 10

PUBLICIP = '192.198.94.16'


def _clearIpFromAuthorizedHosts(ip, port):
    """
    On the machine we run tests we connect to all virtual machines using the same cloudspace address
    with different ports.This is the intended behavior of using port forwarding
    but this causes problem when trying to use ssh because Same IP address has different fingerprint.
    We need to clear the IP first from authorized hosts every time
    """
    home = expanduser("~")
    knownhostspath = os.path.join(home, '.ssh', 'known_hosts')
    process = subprocess.Popen(['ssh-keygen', '-f', knownhostspath, '-R',
                                '[%s]:%s' % (ip, port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process.communicate()


def _getPackageName(size_id):
    """
    Returns Package cpu/ram in one word using size_id
    """
    if size_id == 1:
        return '512G_1CPU'
    elif size_id == 2:
        return '1G_1CPU'
    elif size_id == 3:
        return '2G_2CPU'
    elif size_id == 4:
        return '4G_2CPU'
    elif size_id == 5:
        return '8G_4CPU'
    elif size_id == 6:
        return '16G_8CPU'


def _get_random_port(exposedmachines):
    exposed_ports = [int(x['publicPort']) for x in exposedmachines]
    for port in range(1024, 30000):
        if port not in exposed_ports:
            return port


def _keyGen(url, username, password):
    try:
        r = requests.get(
            '%s/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (url, username, password))
        return r.json()
    except:
        if username is 'operations':
            return 'ae7927e27f6743679b903d0adc1697d0'
        else:
            raise


def createMachine(id, imageid, disksize, sizeid, authkey):
    name = "%s.Test.%s" % (str(id), uuid.uuid4())
    createurl = ('%s/restmachine/cloudapi/machines/create?cloudspaceId=%s&name=%s&' +
                 'description=&sizeId=%s&imageId=%s&disksize=%s&authkey=%s') % (
        URL, CLOUD_SPACE_ID, name, sizeid, imageid, disksize, authkey)
    res = requests.get(createurl)
    if not res.ok:
        raise Exception(res.text)
    print "Created: %s" % name
    sys.stdout.flush()
    return res.json()


def exposeMachine(machineid, authkey):
    # Make sure Machine has Ip address
    getMachine(machineid, authkey)

    listurl = '%s/restmachine/cloudapi/portforwarding/list?cloudspaceid=%s&protocol=tcp&authkey=%s' % (
        URL, CLOUD_SPACE_ID, authkey)

    res = requests.get(listurl)
    if not res.ok:
        raise Exception(res.text)

    publicport = _get_random_port(res.json())

    exposeurl = ('%s/restmachine/cloudapi/portforwarding/create?cloudspaceid=%s&' +
                 'protocol=tcp&localPort=22&vmid=%s&publicIp=%s&publicPort=%s&authkey=%s') % (
        URL, CLOUD_SPACE_ID, machineid, PUBLICIP, publicport, authkey)
    res = requests.get(exposeurl)
    if not res.ok:
        raise Exception(res.text)
    print "Exposed machine: %s through IP %s and port %s" % (str(machineid), PUBLICIP, str(publicport))
    sys.stdout.flush()
    return publicport


def getMachine(machineid, authkey):
    host = 'Undefined'
    vm = None
    while host == 'Undefined':
        print "Trying to Get IP address for machine : %s" % machineid
        sys.stdout.flush()
        time.sleep(5)
        geturl = '%s/restmachine/cloudapi/machines/get?machineId=%s&authkey=%s' % (
            URL, machineid, authkey)
        res = requests.get(geturl)
        vm = res.json()
        host = vm['interfaces'][0]['ipAddress']
    print "IP address is retrieved"
    sys.stdout.flush()
    return vm


def installAndRunUnixBench(machineids, authkey, hosts_public_ports):
    for machineid in machineids:
        sshhost = PUBLICIP
        sshport = hosts_public_ports[machineid]
        _clearIpFromAuthorizedHosts(sshhost, sshport)

        print "Installing UnixBench on machine %s" % str(machineid)
        sys.stdout.flush()
        vm = getMachine(machineid, authkey)
        sshpassword = vm['accounts'][0]['password']
        sshusername = vm['accounts'][0]['login']

        host_string = '%s@%s:%s' % (sshusername, sshhost, sshport)
        env.passwords[host_string] = sshpassword
        with settings(host_string=host_string):
            sudo('apt-get install -y tmux gcc make')
            run('wget https://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz')
            run('tar -xf UnixBench5.1.3.tgz')
            with cd('UnixBench'):
                run('make')
                run('tmux new-session -s Test -d "echo %s | sudo -S ./Run >> UnixBench5screen"' % sshpassword)


def collectNixStats(machineids, authkey, hosts_public_ports):
    """
    fab -H 192.198.94.16 -u cloudscalers -p r48mC47bD --port 23 -- 'cat UnixBench/UnixBench5screen |
        grep -i "System Benchmarks Index Score" |  grep -o [0-9].*'
    """
    result_single = []
    result_multi = []
    for machineid in machineids:
        sshhost = PUBLICIP
        sshport = hosts_public_ports[machineid]
        _clearIpFromAuthorizedHosts(sshhost, sshport)
        print "Collecting Statistics for machine %s" % str(machineid)
        sys.stdout.flush()
        vm = getMachine(machineid, authkey)
        sshpassword = vm['accounts'][0]['password']
        sshusername = vm['accounts'][0]['login']

        fabb_conn = ('fab -H %s -u %s -p %s --port=%s -- cat UnixBench/UnixBench5screen |' +
                     ' grep -i "System Benchmarks Index Score" |  grep -o [0-9].*') % (
            sshhost, sshusername, sshpassword, sshport)
        output = ""
        try:
            output = commands.getoutput(fabb_conn)
        except:
            print "Error -- Can't collect statistics"
            sys.stdout.flush()
            return []
        result = output.split()
        indexes = [i for i, x in enumerate(result) if x == 'Score']
        if len(indexes) == 1:
            scoresingle = result[indexes[0] + 1]
            result_single.append(scoresingle)
        elif len(indexes) == 2:
            scoresingle = result[indexes[0] + 1]
            scoremulti = result[indexes[1] + 1]
            result_single.append(scoresingle)
            result_multi.append(scoremulti)
        else:
            raise ("Invslid data" + output)
    final = [reduce(add, [float(x)
                          for x in result_single]) / len(result_single)]
    if result_multi:
        m = reduce(add, [float(x) for x in result_multi]) / len(result_multi)
        final.append(m[0])
    return final


def generateStatsCSVs(stats):
    """
    stats = {'ubuntu':{1GB_1CPU:[.9]}}
    """
    print "Generating CSVs"
    sys.stdout.flush()
    for system, packagestat in stats.iteritems():
        for packagename, values in packagestat.iteritems():
            cwd = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(cwd, '%s.%s.csv' % (system, packagename))
            csv_file = open(filename, 'wa')
            csv_out = csv.writer(csv_file, delimiter=',')
            if not len(values):
                continue
            elif len(values) == 1:
                csv_out.writerow(['One Single Run'])
                csv_out.writerow([values[0]])
            else:
                csv_out.writerow(
                    ['One Single Run', 'Parallel Runs across all cores'])
                csv_out.writerow([values[0], values[1]])


def test(win_count=0, linux_count=0):
    try:
        win_count = int(win_count)
        linux_count = int(linux_count)

        authkey = _keyGen(URL, USERNAME, PASSWORD)
        machines = {'ubuntu': {}, 'windows': {}}
        stats = {'ubuntu': {}, 'windows': {}}
        public_ports = {}
        for sizeid in UBUNNTU_SIZE_IDS:
            packagename = _getPackageName(sizeid)
            machines['ubuntu'].setdefault(packagename, [])
            stats['ubuntu'].setdefault(packagename, [])

            for i in range(linux_count):
                mid = createMachine(
                    i, UBUNTU_IMAGE_ID, UBUNTU_DISK_SIZE, sizeid, authkey)
                pubport = exposeMachine(mid, authkey)
                public_ports[mid] = pubport
                machines['ubuntu'][packagename].append(mid)

        # for sizeif in WINDOWS_SIZE_IDS:
        #     for i in range(win_count):
        #         mid = createMachine(
        #             i, WINDOWS_IMAGE_ID, WINDOWS_DISK_SIZE, sizeid, authkey)
        #         pubport = exposeMachine(mid, authkey)
        #         public_ports[mid] = pubport
        #         machines['windows'][packagename].append(mid)

        # Install benchmark on all machines
        all_linux_machines = []
        for v in machines['ubuntu'].itervalues():
            all_linux_machines.extend(v)

        installAndRunUnixBench(all_linux_machines, authkey, public_ports)

#         for packagename in machines['ubuntu'].keys():
#             stats['ubuntu'][packagename] = collectNixStats(
#                 machines['ubuntu'][packagename], authkey, public_ports)
# #             STATS['ubuntu'][packagename] =  collectNixStats([169], authkey, public_ports)

#         generateStatsCSVs(stats)

    except (ValueError, IndexError):
        print "USAGE: python loadtests.py numOfwindowsmachines numOfLinuxMachines"
        sys.stdout.flush()
