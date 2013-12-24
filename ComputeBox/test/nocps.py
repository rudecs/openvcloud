import xmlrpclib
import time

def installFreshComputeNode(nocps_url, macaddress, hostname):
    print 'Installing Ubuntu 13.10 on the compute node'
    
    ps = xmlrpclib.ServerProxy(nocps_url)
    
    serverdetails = {
                     'adminuser': 'cs',
                     'hostname': hostname,
                     'mac': macaddress,    #Physical machine identifier
                     'profile': 649,                #Ubuntu 13.10, cloudscalers apt-get server
                     'rebootmethod': 'auto',
                     'rootpassword': 'R00t3r',
                     'rootpassword2': 'R00t3r',
                     'userpassword': 'cs',
                     'userpassword2': 'cs'}
    
    provisioning_result = ps.PXE_API.provisionHost(serverdetails)
    if not provisioning_result['success']:
        print provisioning_result
    
    laststatus = ""
    while True:
        status = ps.PXE_API.getProvisioningStatusByServer(macaddress)
        if status:
            line = "%(statusmsg)s: %(statusprogress)s " % (status)
            if line != laststatus:
                print line
                laststatus = line
        else:
            print 'Done'
            break
        time.sleep(5)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--url',required=True, help='Url of nocps xmlrpc server like https://user:password@nocps.incubaid.com/xmlrpc.php')
    parser.add_argument('-m','--mac',required=True, help='MAC address of the server to be reinstalled')
    parser.add_argument('--hostname', required=True, help='Hostname of the server to be reinstalled')
    args = parser.parse_args()
    
    installFreshComputeNode(args.url, args.mac, args.hostname)
