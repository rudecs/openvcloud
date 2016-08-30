from JumpScale import j
import sys
import re

#
# must be run on ovcgit
#

def enableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = False
    j.remote.cuisine.api.fabric.state.output['running'] = False

def disableQuiet():
    j.remote.cuisine.api.fabric.state.output['stdout'] = True
    j.remote.cuisine.api.fabric.state.output['running'] = True



openvcloud = j.clients.openvcloud.get()
nodes = openvcloud.getRemoteNodes()

hardware = {'unknown': [], 'CPU': [], 'Storage': []}

enableQuiet()

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
    
    if 'storagenode' in hrd.get('node.roles'):
        hwd['role'] = 'Storage'

    if 'cpunode' in hrd.get('node.roles'):
        hwd['role'] = 'CPU'
    
    hardware[hwd['role']].append(hwd)
    

#
# Formatter
#
types = ['CPU', 'Storage']

print("# CPU")
for t in types:
    print("## %s Nodes" % t)
    print("| Node | Cores | Model |")
    print("|------|-------|-------|")
    total = 0

    for host in hardware[t]:
        print("| `%s` | %s | %s |" % (host['hostname'], host['cpu-cores'], host['cpu-model']))
        total += int(host['cpu-cores'])

    print("| **Total** | **%d** | |" % total)



print("")
print("# Memory")
for t in types:
    print("## %s Nodes" % t)
    print("| Node | RAM installed |")
    print("|------|---------------|")
    total = 0

    for host in hardware[t]:
        print("| `%s` | %.1f GiB |" % (host['hostname'], int(host['ram-mb']) / 1024.0))
        total += int(host['ram-mb'])

    print("| **Total** | **%.2f TiB** |" % (int(total) / 1024.0 / 1024.0))



print("")    
print("# Disks")
for t in types:
    print("## %s Nodes: SSD" % t)
    print("")
    print("| Node | Device | Model | Size |")
    print("|------|--------|:-----:|-----:|")
    total = 0
    
    for host in hardware[t]:
        for x in host['disks']['ssd']:
            gb = int(x['size']) / (1024 * 1024 * 1024)
            print("| `%s` | `%s` | %s | %.2f GiB |" % (host['hostname'], x['device'], x['model'], gb))
            total += float(gb)
    
    print("|  |  | **Total** | **%.2f TiB** |" % (float(total) / 1024.0))
    print("")


for t in types:
    print("## %s Nodes: HDD" % t)
    print("")
    print("| Node | Device | Model | Size |")
    print("|------|--------|:-----:|-----:|")
    total = 0
    
    for host in hardware[t]:
        for x in host['disks']['hdd']:
            gb = int(x['size']) / (1024 * 1024 * 1024)
            print("| `%s` | `%s` | %s | %.2f GiB |" % (host['hostname'], x['device'], x['model'], gb))
            total += float(gb)
    
    print("|  |  | **Total** | **%.2f TiB** |" % (float(total) / 1024.0))
    print("")
