import sys
import requests
import uuid
import time
import commands
import csv
from operator import add
import os
from fabric.api import env, run, sudo, cd, settings

class HTTP(object):
    @staticmethod
    def parse_response(response):
        """
        @param response: HTTP Response object coming from requests lib response
        @raise exception: If response not OK
        """
        if response.ok:
            return response.json()
        raise Exception('HTTP Error: %s' % response.text)

class CloudSpace(object):
    def __init__(self,
                 id,
                 host,
                 username,
                 passwd,
                 publicip,
                 ubuntu_size_ids,
                 windows_size_ids,
                 ubuntu_image_id,
                 windows_image_id,
                 ubuntu_disk_size,
                 windows_disk_size):
        
        self.id = id
        self.host = host
        self.username = username
        self.passwd = passwd
        self.publicip = publicip
        self.ubuntu_size_ids = ubuntu_size_ids
        self.windows_size_ids = windows_size_ids
        self.ubuntu_image_id = ubuntu_image_id
        self.windows_image_id = windows_image_id
        self.ubuntu_disk_size = ubuntu_disk_size
        self.windows_disk_size = windows_disk_size
        self._ubuntu_machines = {}
        self._windows_machines = {}

        self.auth_url = '%s/restmachine/cloudapi/users/authenticate?username=%s&password=%s' % (
            host, username, passwd)
        
        self.portforwardlist_url = '%s/restmachine/cloudapi/portforwarding/list?cloudspaceid=%s&protocol=tcp&authkey=%s' % (
            host, id, self.authkey)
        
    
    @property
    def authkey(self):
        """
        Generates authkey for this cloudspace and caches it for further usage.
        """
        if not hasattr(self, '_authkey'):
            key = HTTP.parse_response(requests.get(self.auth_url))
            setattr(self, '_authkey', key)
        return self._authkey

    @staticmethod
    def get(cloudspacename):

        if cloudspacename == 'lenoire1':
            return CloudSpace(id=91,
                              host='http://cpu01.lenoir1.vscalers.com/',
                              username='loadtester',
                              passwd='rooterR00t3r',
                              publicip='192.198.94.16',
                              ubuntu_size_ids=[2],
                              windows_size_ids=[4],
                              ubuntu_image_id=2,
                              windows_image_id=6,
                              ubuntu_disk_size=10,
                              windows_disk_size=20)
            
        elif cloudspacename == 'demo1':
            return CloudSpace(id=11,
                              host='https://demo1.demo.greenitglobe.com',
                              username='hamdy',
                              passwd='changeme',
                              publicip='10.101.135.8',
                              ubuntu_size_ids=[2],
                              windows_size_ids=[4],
                              ubuntu_image_id=1,
                              windows_image_id=2,
                              ubuntu_disk_size=10,
                              windows_disk_size=20)
    
    def get_Package_name(self, size_id):
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
        
    def get_available_port(self, cache=True):
        """
        @param cache: cache last available port in order to increment by 1 in next call
        @warning: caching is suitable only if no other one runs tests on that cloudspace.
        Returns the next available public port for a machines to use it in
        port forwarding.
        """
        if not hasattr(self, '_last_pub_port'):
            portforwards = [ int(p['publicPort']) for p in HTTP.parse_response(requests.get(self.portforwardlist_url))]
            for port in range(1023, 30000):
                if port + 1 not in portforwards:
                    setattr(self, '_last_pub_port', port)
                    break
        self._last_pub_port += 1
        return self._last_pub_port
    
    def register_machine(self, machine):
        packagename = self.get_Package_name(machine.sizeid)
        if machine.type == 'ubuntu':
            self._ubuntu_machines[packagename] = self._ubuntu_machines.get(packagename, [])
            self._ubuntu_machines[packagename].append(machine)
        else:
            self._windows_machines[packagename] = self._windows_machines.get(packagename, [])
            self._windows_machines[packagename].append(machine)
            
    @property
    def ubuntu_machines(self):
        res = []
        for machine_list in self._ubuntu_machines.values():
            for machine in machine_list:
                res.append(machine)
        return res
    
    @property
    def windows_machines(self):
        res = []
        for machine_list in self._windows_machines.values():
            for machine in machine_list:
                res.append(machine)
        return res
    
    def install_benchmark_tool(self):
        for machine in self.ubuntu_machines + self.windows_machines:
            machine.install_benchmark_tool()
            
    def statistics(self):
        stats = {'ubuntu':{}, 'windows':{}}
        for machine in self.ubuntu_machines + self.windows_machines:
            packagename = self.get_Package_name(machine.sizeid)
            stats[machine.type][packagename] = stats[machine.type].get(packagename, [])
            stats[machine.type][packagename] = machine.statistics()
        return stats
    
    def csvs(self, stats):
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
    
class VM(object):
    """
    Parent class representing a remote virtual machine
    """
    def __init__(self, cloudspace, sizeid, imageid, disksize):
        """
        @param id: changes from 0 to number when machine is actually created remotely
        """
        self.id = id = 0
        self.cloudspace = cloudspace
        self.publicport = cloudspace.get_available_port(cache=True)
        self._name = None
        self.ip = None
        self.username = None
        self.passwd = None
        self._info = None
        self.imageid = imageid
        self.sizeid = sizeid
        self.disksize = disksize
        self.create_url = ('%s/restmachine/cloudapi/machines/create?cloudspaceId=%s&name=%s&' +
            'description=&sizeId=%s&imageId=%s&disksize=%s&authkey=%s') % (
                cloudspace.host, cloudspace.id, self.name, sizeid, imageid, disksize, cloudspace.authkey)
    
    @property
    def name(self):
        if not self._name:
            self._name = uuid.uuid4()
        return self._name
    
    @property
    def type(self):
        if self.imageid == self.cloudspace.ubuntu_image_id:
            return 'ubuntu'
        else:
            return 'windows'

    @property
    def info_url(self):
        if not self.id:
            raise Exception('Machine not created yet')
        return '%s/restmachine/cloudapi/machines/get?machineId=%s&authkey=%s' % (
                self.cloudspace.host, self.id, self.cloudspace.authkey)
    
    @property
    def portforwardcreate_url(self):
        if not self.id:
            raise Exception('Machine not created yet')
        return ('%s/restmachine/cloudapi/portforwarding/create?cloudspaceid=%s&' +
            'protocol=tcp&localPort=22&vmid=%s&publicIp=%s&publicPort=%s&authkey=%s') % (
                self.cloudspace.host, self.cloudspace.id, self.id, self.cloudspace.publicip, self.publicport, self.cloudspace.authkey)

    def set_info(self):
        self.log('retrieving info', 'WAITING')
        if not self._info:
            ip = 'Undefined'
            while ip == 'Undefined':
                time.sleep(5)
                self._info = HTTP.parse_response(requests.get(self.info_url))
                ip = self._info['interfaces'][0]['ipAddress']

        self.log('retrieving info', 'OK')
        self.ip = self._info['interfaces'][0]['ipAddress']
        self.passwd = self._info['accounts'][0]['password']
        self.username = self._info['accounts'][0]['login']
        
    def expose(self):
        self.log('exposing publicly', 'WAITING')
        try:
            HTTP.parse_response(requests.get(self.portforwardcreate_url))
        except:
            # Some how publicport is taken by another dude playing around with the cloudspace
            self.publicport = self.cloudspace.get_available_port(cache=False)
            HTTP.parse_response(requests.get(self.portforwardcreate_url))
        
        self.log('exposing publicly', 'OK')
        self.log('info', 'IP=%s port=%s username=%s password=%s' % (
            self.cloudspace.publicip, self.publicport, self.username, self.passwd))
        
    def log(self, message, status=''):
        """
        Prints log messages and flush stdout (important for jenkins to display messages)
        """
        print "Machine %i : %s : %s" % (self.id, message, status)
        sys.stdout.flush()
        
    def register_in_cloudspace(self):
        self.cloudspace.register_machine(self)
    
    def create(self):
        if self.id:
            raise Exception('Machine %i already created' % self.id)
        self.id = HTTP.parse_response(requests.get(self.create_url))
        self.log('creating', 'OK')
        self.set_info()
        self.expose()
        self.register_in_cloudspace()
        return self.id
    
    def _install_unixbench(self):
        self.log('Installing UnixBench', 'WAITING')
        host_string = '%s@%s:%s' % (self.username, self.cloudspace.publicip, self.publicport)
        env.passwords[host_string] = self.passwd
        
        with settings(host_string=host_string):
            sudo('apt-get install -y tmux gcc make')
            run('wget https://byte-unixbench.googlecode.com/files/UnixBench5.1.3.tgz')
            run('tar -xf UnixBench5.1.3.tgz')
            with cd('UnixBench'):
                run('make')
                run('tmux new-session -s Test -d "echo %s | sudo -S ./Run >> UnixBench5screen"' % self.passwd)

    def _install_winbench(self):
        pass
    
    def install_benchmark_tool(self):
        if self.type == 'ubuntu':
            self._install_unixbench()
        else:
            self._install_winbench()
    
    def _collect_nix_stats(self):
        
        result_single = []
        result_multi = []
        fabb_conn = ('fab -H %s -u %s -p %s --port=%s -- cat UnixBench/UnixBench5screen |' +
                     ' grep -i "System Benchmarks Index Score" |  grep -o [0-9].*') % (
                            self.cloudspace.publicip, self.username, self.passwd, self.publicport)
        output = ""
        try:
            output = commands.getoutput(fabb_conn)
        except:
            self.log('Collecting statistics', 'NOT OK %s' % output)
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
            self.log('Collecting statistics', 'NOT OK\n%s' % output)
            return []
        final = [reduce(add, [float(x)
                              for x in result_single]) / len(result_single)]
        if result_multi:
            m = reduce(add, [float(x) for x in result_multi]) / len(result_multi)
            final.append(m)
        self.log('Collecting statistics', 'OK')
        return final
    
    def _collect_windows_stats(self):
        pass
    
    def statistics(self):
        self.log('Collecting statistics', 'WAITING')
        if self.type == 'ubuntu':
            return self._collect_nix_stats()
        else:
            return self._collect_windows_stats()

def test(cloudspacename='demo1', win_count=0, linux_count=0):
    try:
        win_count = int(win_count)
        linux_count = int(linux_count)
    except ValueError:
        print "win_count & linux_count arguments must be integers"
    
    cl = CloudSpace.get(cloudspacename)
    
    for sizeid in cl.ubuntu_size_ids:
        for _ in range(linux_count):
            machine  = VM(cl, sizeid, cl.ubuntu_image_id, cl.ubuntu_disk_size)
            machine.create()
 
    for sizeid in cl.windows_size_ids:
        for _ in range(win_count):
            machine  = VM(cl, sizeid, cl.windows_image_id, cl.windows_disk_size)
            machine.create()
    cl.install_benchmark_tool()
    # Wait a little before collecting statistics
    time.sleep(35*60)
    statistics = cl.statistics()
    cl.csvs(statistics)