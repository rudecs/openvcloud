import xmlrpclib
import time

def installFreshComputeNode(nocps_url, macaddress, hostname, ip, profilename):
    print 'Installing %s on the compute node' % profilename

    ps = xmlrpclib.ServerProxy(nocps_url)
    if not macaddress or not ip:
        hosts = ps.PXE_API.searchHosts({'query': hostname})['data']
        for host in hosts:
            if host['hostname'] == hostname:
                macaddress = host['mac']
                break
    elif not macaddress:
        macaddress = ps.PXE_API.getServerByIP(ip)
    profile = ps.PXE_API.getProfileByName(profilename)

    serverdetails = {
                     'adminuser': 'cs',
                     'hostname': hostname,
                     'mac': macaddress,    #Physical machine identifier
                     'profile': profile,                #Ubuntu 14.04, cloudscalers apt-get server
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
    parser.add_argument('-m','--mac',required=False, help='MAC address of the server to be reinstalled')
    parser.add_argument('-i','--ip',required=False, help='IP address of the server to be reinstalled')
    parser.add_argument('-p','--profile',required=False, help='Profile to install', default="CloudScalers Ubuntu 14.04")
    parser.add_argument('--hostname', required=True, help='Hostname of the server to be reinstalled')
    args = parser.parse_args()

    installFreshComputeNode(args.url, args.mac, args.hostname, args.ip, args.profile)
