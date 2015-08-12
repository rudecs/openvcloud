import sys
import requests
import uuid
import pxssh
import time
import commands
import csv
from operator import add
import os
import pexpect

URL = 'http://cpu01.lenoir1.vscalers.com/'
USERNAME = 'loadtester'
PASSWORD = 'rooterR00t3r'
CLOUD_SPACE_ID = 91
SIZEIDS = [2]
UBUNTU_IMAGE_ID = 2
WINDOWS_IMAGE_ID = 4
WINDOWS_DISK_SIZE = 16
UBUNTU_DISK_SIZE = 10

PUBLICIP = '192.198.94.16'

def _getPackageName(sizeId):
    """
    Returns Package cpu/ram in one word using sizeID
    """
    if sizeId == 1:
        return '512G_1CPU'
    elif sizeId == 2:
        return '1G_1CPU'
    elif sizeId == 3:
        return '2G_2CPU'
    elif sizeId == 4:
        return '4G_2CPU'
    elif sizeId == 5:
        return '8G_4CPU'
    elif sizeId == 6:
        return '16G_8CPU'

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
    createurl = '%s/restmachine/cloudapi/machines/create?cloudspaceId=%s&name=%s&description=&sizeId=%s&imageId=%s&disksize=%s&authkey=%s' % (
            URL, CLOUD_SPACE_ID, name, sizeid, imageid, disksize, authkey)
    res = requests.get(createurl)
    if not res.ok:
        raise Exception(res.text)
    print "Created: %s" % name
    sys.stdout.flush()
    return res.json()

def exposeMachine(machineid, publiport, authkey):
    exposeurl = '%s/restmachine/cloudapi/portforwarding/create?cloudspaceid=%s&protocol=tcp&localPort=22&vmid=%s&publicIp=%s&publicPort=%s&authkey=%s' % (
            URL, CLOUD_SPACE_ID, machineid, PUBLICIP, publiport, authkey)
    
    # Make sure machine has IP address
    vm = getMachine(machineid, authkey)
    res = requests.get(exposeurl)
    if not res.ok:
        raise Exception(res.text)
    print "Exposed machine: %s through IP %s and port %s" % (str(machineid),PUBLICIP, str(publiport))
    sys.stdout.flush()
    return res.json()

def getMachine(machineid, authkey):
    host = 'Undefined'
    vm = None
    while host == 'Undefined':
        print "Trying to Get IP address for machine : %s" % machineid
        sys.stdout.flush()
        time.sleep(5)
        geturl = '%s/restmachine/cloudapi/machines/get?machineId=%s&authkey=%s' % (URL, machineid, authkey)
        res = requests.get(geturl)
        vm = res.json()
        host = vm['interfaces'][0]['ipAddress']
    print "IP address is retrieved"
    sys.stdout.flush()
    return vm

def installAndRunUnixBench(machineids, authkey, hosts_public_ports):
    for machineid in machineids:
        sshport = hosts_public_ports[machineid]
        print "Installing UnixBench on machine %s" % str(machineid)
        sys.stdout.flush()
        vm = getMachine(machineid, authkey)
        sshpassword = vm['accounts'][0]['password']
        sshusername = vm['accounts'][0]['login']
        sshhost = PUBLICIP
        ssh_newkey = 'Are you sure you want to continue connecting'
        p=pexpect.spawn('ssh %s@%s -p %s' % (sshusername, sshhost, sshport))
        i=p.expect([ssh_newkey,'password:',pexpect.EOF])
        if i==0:
            print "Continue connection"
            p.sendline('yes')
        
        ssh = pxssh.pxssh()
        if not ssh.login(sshhost, sshusername, sshpassword, port=sshport):
            print "SSH session failed on login."
            print str(ssh)
        else:
            print "SSH session login successful"
            ssh.sendline('echo %s | sudo -S apt-get install tmux' % sshpassword)
            ssh.prompt()
            print ssh.before
            ssh.sendline('wget https://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz')
            ssh.prompt()
            print ssh.before
            ssh.sendline('tar -xzvf UnixBench5.1.3.tgz')
            ssh.prompt()
            print ssh.before
            ssh.sendline('echo %s | sudo -S apt-get install -y gcc make' % sshpassword)
            ssh.prompt()
            print ssh.before
            ssh.sendline('cd UnixBench')
            ssh.prompt()
            print ssh.before
            ssh.sendline('echo %s | sudo -S make' % sshpassword)
            ssh.prompt()
            print ssh.before
            ssh.sendline('tmux new-session -s Test -d "echo %s | sudo -S ./Run >> UnixBench5screen"' % sshpassword)
            ssh.prompt()
            print ssh.before
            ssh.logout()
        
def collectNixStats(machineids, authkey, hosts_public_ports):
    result_single = []
    result_multi = []
    for machineid in machineids:
        sshport = hosts_public_ports[machineid]
        print "Collecting Statistics for machine %s" % str(machineid)
        sys.stdout.flush()
        vm = getMachine(machineid, authkey)
        sshpassword = vm['accounts'][0]['password']
        sshusername = vm['accounts'][0]['login']
        sshhost = PUBLICIP
        fabb_conn = 'fab -H %s -u %s -p %s --port=%s -- cat UnixBench/UnixBench5screen | grep -i "System Benchmarks Index Score" |  grep -o [0-9].*' % (
            sshhost, sshusername, sshpassword, sshport)
        output = commands.getoutput(fabb_conn)
        result = output.split()
        indexes = [i for i,x in enumerate(result) if x == 'Score']
        if len(indexes) == 1:
            scoresingle = result[indexes[0]+1]
            result_single.append(scoresingle)
        elif len(indexes) == 2:
            scoresingle = result[indexes[0]+1]
            scoremulti = result[indexes[1]+1]
            result_single.append(scoresingle)
            result_multi.append(scoremulti)
        else:
            raise  ("Invslid data" + output)
    final = [reduce(add, [float(x) for x in result_single]) / len(result_single)]
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
                csv_out.writerow(['One Single Run', 'Parallel Runs across all cores'])
                csv_out.writerow([values[0], values[1]])

if __name__ == '__main__':
    try:
        winMachinesCount = int(sys.argv[1])
        linuxMachinesCount = int(sys.argv[2])
        total = winMachinesCount + linuxMachinesCount
        authkey = _keyGen(URL, USERNAME, PASSWORD)
        MACHINES = {'ubuntu':{}, 'windows':{}}
        STATS = {'ubuntu':{}, 'windows':{}}
        PUBLIC_PORTS = {}
        for sizeid in SIZEIDS:
            packagename = _getPackageName(sizeid)
            MACHINES['ubuntu'][packagename] = []
            MACHINES['windows'][packagename] = []
            STATS['ubuntu'][packagename] = []
            STATS['windows'][packagename] = []

            for i in range(linuxMachinesCount):
                mid = createMachine(i, UBUNTU_IMAGE_ID, UBUNTU_DISK_SIZE, sizeid, authkey)
                pubport = 23 + i
                exposeMachine(mid, pubport, authkey)
                PUBLIC_PORTS[mid] = pubport
                MACHINES['ubuntu'][packagename].append(mid)
        
        # Install benchmark on all machines
        all_linux_machines = []
        for _, v in MACHINES['ubuntu'].iteritems():
            all_linux_machines.extend(v)
        installAndRunUnixBench(all_linux_machines, authkey, PUBLIC_PORTS)

        for packagename in MACHINES['ubuntu'].keys():
#             STATS['ubuntu'][packagename] =  collectNixStats(MACHINES['ubuntu'][packagename], authkey, PUBLIC_PORTS)
            STATS['ubuntu'][packagename] =  collectNixStats([116], authkey, PUBLIC_PORTS)
    
        generateStatsCSVs(STATS)
        
    except (ValueError, IndexError):
        print "USAGE: python loadtests.py numOfwindowsmachines numOfLinuxMachines"
        sys.stdout.flush()
