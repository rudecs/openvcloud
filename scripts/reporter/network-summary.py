import subprocess

#
# must be run on controller
#

class NetworkSummary():
    def __init__(self):
        # keep interface
        self._kintf = ['mgmt', 'backplane1']
        
        # local data
        self._intf = {}
        self._nodes = []
    
    def interfaces(self):
        proc = subprocess.Popen(['ip', '-o', '-4', 'addr', 'show'], stdout=subprocess.PIPE)
        output = []
        
        for input in proc.stdout:
            output.append(input.decode('utf-8').rstrip().split(" "))

        for intf in output:
            if intf[1] in self._kintf:
                self._intf[intf[1]] = intf[6]
        
        return self._intf
    
    def nodes(self):
        with open("/opt/g8-pxeboot/pxeboot/conf/hosts") as f:
            hosts = f.read()
        
        with open("/opt/g8-pxeboot/pxeboot/conf/dhcphosts") as f:
            dhcphosts = f.read()
        
        # building dhcp table
        lines = dhcphosts.split("\n")
        dhcp = {}
        
        for line in lines:
            if line.startswith('#') or line == '':
                continue
            
            temp = line.split(',')
            dhcp[temp[1]] = temp[0]
        
        lines = hosts.split("\n")
        for line in lines:
            if line == '':
                continue
            
            items = line.split(" ")
            
            if not dhcp.get(items[2]):
                continue
            
            self._nodes.append({
                'name': items[1],
                'address': items[0],
                'mac': dhcp[items[2]]
            })
        
        return self._nodes
    
    def markdown(self):
        print("# Interfaces")
        print("| Name | Address |")
        print("| ---- | ------- |")

        for intf in self._intf:
            print("| %s | %s |" % (intf, self._intf[intf]))
        
        print("")
        
        print("# Nodes configured")
        print("| Name | MAC Address | IP Address | ")
        print("| ---- | ----------- | ---------- | ")
        
        for node in self._nodes:
            print("| %s | `%s` | `%s` |" % (node['name'], node['mac'], node['address']))
        
        print("")
        
        print("# Routing, Switching")
        print("...")
    
net = NetworkSummary()

net.interfaces()
net.nodes()

net.markdown()
