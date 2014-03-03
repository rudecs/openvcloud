import sys
import socket
import rosapi
from netaddr import EUI

class routeros(): 
     
    def __init__(self, ipaddress):
        self.ipaddress = ipaddress
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.ipaddress, 8728))
        self.api = rosapi.RosAPI(self.sock)
        self.api.login(b'api', b'api')

    def leaseExists(self, macaddress):
        if self.getLease(macaddress):
            return True
        else:
            return False
    
    def getLease(self, macaddress):
        leases = self.api.talk([b'/ip/dhcp-server/lease/print'])
        for i, lease in leases:
             if 'mac-address' in lease and EUI(lease['mac-address'])== EUI(macaddress):
                 return lease
        return None
    
    def getIpaddress(self, macaddress):
        lease = self.getLease(macaddress)
        if lease and 'address' in lease.keys():
            return lease['address']
        return None
    
    def close(self):
        self.sock.close()
        
        
            

    












