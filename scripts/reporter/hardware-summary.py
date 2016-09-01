from JumpScale import j
import sys
import re
import StringIO

#
# must be run on ovcgit
#
class HardwareSummary():
    def __init__(self):
        self.writer = StringIO.StringIO()
        self.hardware = {'unknown': [], 'CPU': [], 'Storage': []}
        
    def _enableQuiet(self):
        j.remote.cuisine.api.fabric.state.output['stdout'] = False
        j.remote.cuisine.api.fabric.state.output['running'] = False

    def _disableQuiet():
        j.remote.cuisine.api.fabric.state.output['stdout'] = True
        j.remote.cuisine.api.fabric.state.output['running'] = True

    def log(self, line):
        self.writer.write(line + "\n")

    def retrieve(self):
        openvcloud = j.clients.openvcloud.get()
        nodes = openvcloud.getRemoteNodes()

        self._enableQuiet()

        #
        # Grabbing data
        #

        for service in nodes:
            hwd = {'hostname': service.instance}
            
            sys.stderr.write("Loading: %s\n" % service.instance)
            
            ssh = j.atyourservice.get(name='node.ssh', instance=service.instance)
            cpu = ssh.execute("grep model\ name /proc/cpuinfo | cut -d: -f2")
            mem = ssh.execute("grep MemTotal /proc/meminfo")
            dsk = ssh.execute('lsblk -P -n -b -o NAME,ROTA,SIZE,MODEL,TYPE')
            grd = ssh.execute('cat /opt/jumpscale7/hrd/system/grid.hrd') + "\n\n"

            #
            # CPU
            #
            nbcpu = len(cpu.split("\n"))
            model = cpu.split("\n")[0].strip()
            
            hwd['cpu-cores'] = int(nbcpu)
            hwd['cpu-model'] = model
            
            #
            # Memory (RAM)
            #
            temp = mem.split(' ')
            ram = temp[-2]
            
            hwd['ram-mb'] = int(ram) / 1024
            
            #
            # Disks
            #
            disks = {'ssd': [], 'hdd': []}
            temp = dsk.split("\r\n")
            
            for line in temp:
                # skip partition
                if 'TYPE="part"' in line:
                    continue
                
                disk = re.compile('="|" |"$').split(line)
                type = 'hdd' if disk[3] == "1" else 'ssd'
                
                disks[type].append({
                    'device': disk[1],
                    'size': disk[5],
                    'model': disk[7]
                })
            
            hwd['disks'] = disks
            
            hrd = j.core.hrd.get(content=grd)
            hwd['roles'] = 'unknown'
            r = hrd.get('node.roles')
            
            if 'storagenode' in r or 'storagedriver' in r:
                hwd['role'] = 'Storage'

            if 'cpunode' in r:
                hwd['role'] = 'CPU'
            
            self.hardware[hwd['role']].append(hwd)

    def generate(self):
        types = ['CPU', 'Storage']

        self.log("# CPU")
        for t in types:
            self.log("## %s Nodes" % t)
            self.log("| Node | Cores | Model |")
            self.log("|------|-------|-------|")
            total = 0

            for host in self.hardware[t]:
                self.log("| `%s` | %s | %s |" % (host['hostname'], host['cpu-cores'], host['cpu-model']))
                total += int(host['cpu-cores'])

            self.log("| **Total** | **%d** | |" % total)



        self.log("")
        self.log("# Memory")
        for t in types:
            self.log("## %s Nodes" % t)
            self.log("| Node | RAM installed |")
            self.log("|------|---------------|")
            total = 0

            for host in self.hardware[t]:
                self.log("| `%s` | %.1f GiB |" % (host['hostname'], int(host['ram-mb']) / 1024.0))
                total += int(host['ram-mb'])

            self.log("| **Total** | **%.2f TiB** |" % (int(total) / 1024.0 / 1024.0))



        self.log("")    
        self.log("# Disks")
        for t in types:
            self.log("## %s Nodes: SSD" % t)
            self.log("")
            self.log("| Node | Device | Model | Size |")
            self.log("|------|--------|:-----:|-----:|")
            total = 0
            
            for host in self.hardware[t]:
                for x in host['disks']['ssd']:
                    gb = int(x['size']) / (1024 * 1024 * 1024)
                    self.log("| `%s` | `%s` | %s | %.2f GiB |" % (host['hostname'], x['device'], x['model'], gb))
                    total += float(gb)
            
            self.log("|  |  | **Total** | **%.2f TiB** |" % (float(total) / 1024.0))
            self.log("")


        for t in types:
            self.log("## %s Nodes: HDD" % t)
            self.log("")
            self.log("| Node | Device | Model | Size |")
            self.log("|------|--------|:-----:|-----:|")
            total = 0
            
            for host in self.hardware[t]:
                for x in host['disks']['hdd']:
                    gb = int(x['size']) / (1024 * 1024 * 1024)
                    self.log("| `%s` | `%s` | %s | %.2f GiB |" % (host['hostname'], x['device'], x['model'], gb))
                    total += float(gb)
            
            self.log("|  |  | **Total** | **%.2f TiB** |" % (float(total) / 1024.0))
            self.log("")
    
    def output(self):
        return self.writer.getvalue()


hardware = HardwareSummary()
hardware.retrieve()
hardware.generate()

print("Writing Hardware.md file")
with open('Hardware.md', 'w+') as f:
    f.write(hardware.output())

print("Comitting...")
j.system.process.execute('jspython /opt/code/github/0-complexity/openvcloud/scripts/updates/update-ays.py --commit')
