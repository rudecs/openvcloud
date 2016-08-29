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
            full = f.read()
        
        lines = full.split("\n")
        for line in lines:
            if line == '':
                continue
            
            items = line.split(" ")
            self._nodes.append({'name': items[1], 'address': items[0]})
        
        return self._nodes
    
    def markdown(self):
        print("# Interfaces")
        print("| Name | Address |")
        
        for intf in self._intf:
            print("| %s | %s |" % (intf, self._intf[intf]))
        
        print("")
        
        print("# Nodes configured")
        print("| Name | Address |")
        
        for node in self._nodes:
            print("| %s | %s |" % (node['name'], node['address']))
        
        print("")
        
        print("# Routing, Switching")
        print("...")
    
net = NetworkSummary()

net.interfaces()
net.nodes()

net.markdown()
