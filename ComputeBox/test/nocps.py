import xmlrpclib
import time

def installFreshComputeNode(nocps_url):
    print 'Installing Ubuntu 13.04 on the compute node'
    
    ps = xmlrpclib.ServerProxy(nocps_url)
    macaddress = '00:30:48:fc:23:5d' #'00:e0:81:b2:32:89' #'00:e0:81:b2:89:f9'
    
    serverdetails = {
                     'adminuser': 'cs',
                     'hostname': 'cloudscale52',
                     'mac': macaddress,    #Physical machine identifier
                     'profile': 403,                #Ubuntu 13.04
                     'rebootmethod': 'auto',
                     'rootpassword': 'R00t3r',
                     'rootpassword2': 'R00t3r',
                     'userpassword': 'cs',
                     'userpassword2': 'cs'}
    
    provisioning_result = ps.PXE_API.provisionHost(serverdetails)
    if not provisioning_result['success']:
        print provisioning_result
    
    while ps.PXE_API.getProvisioningStatusByServer(macaddress):
        print '.',
        time.sleep(5)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u','--url',required=True, help='Url of nocps xmlrpc server like https://user:password@nocps.incubaid.com/xmlrpc.php')
    args = parser.parse_args()
    
    installFreshComputeNode(args.url)
