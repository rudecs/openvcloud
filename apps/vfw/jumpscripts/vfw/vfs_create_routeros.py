from JumpScale import j

descr = """
create and start a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
period = 0  # always in sec
enable = True
async = True
queue = 'hypervisor'

def action(networkid, publicip, publicgwip, publiccidr, password):
    import JumpScale.lib.routeros
    import pexpect
    import netaddr
    import libvirt
    import JumpScale.lib.ovsnetconfig
    import time
    import netaddr

    DEFAULTGWIP = j.application.config.get("vfw.default.ip")
    BACKPLANE = 'vxbackend'
    netrange = j.application.config.get("vfw.netrange.internal")
    defaultpasswd=j.application.config.get("vfw.admin.passwd")
    nc = j.system.ovsnetconfig
    con = libvirt.open()

    data = {'nid': j.application.whoAmI.nid,
            'gid': j.application.whoAmI.gid,
            'username': 'vscalers',
            'password': defaultpasswd
            }

    j.packages.findNewest('', 'routeros_config').install()

    networkidHex = '%04x' % int(networkid)
    internalip = str(netaddr.IPAddress(netaddr.IPNetwork(netrange).first + int(networkid)))
    networkname = "space_%s"  % networkidHex
    name = 'routeros_%s' % networkidHex
    destinationdir = '/mnt/vmstor/routeros/%s' % networkidHex



    def cleanup():
        print "CLEANUP: %s/%s"%(networkid,networkidHex)
        try:
            dom = con.lookupByName(name)
            dom.destroy()
            dom.undefine()
        except libvirt.libvirtError:
            pass
        j.system.fs.removeDirTree(destinationdir)
        def deleteNet(net):
            try:
                net.destroy()
            except:
                pass
            try:
                net.undefine()
            except:
                pass
        try:
            for net in con.listAllNetworks():
                if net.name() == networkname:
                    deleteNet(net)
                    break
        except:
            pass

    cleanup()

    try:
        #setup network vxlan
        nc.ensureVXNet(int(networkid), BACKPLANE)
        xml = '''  <network>
        <name>%(networkname)s</name>
        <forward mode="bridge"/>
        <bridge name='%(networkname)s'/>
         <virtualport type='openvswitch'/>
     </network>''' % {'networkname': networkname}
        private = con.networkDefineXML(xml)
        private.create()
        private.setAutostart(True)

        j.system.fs.createDir(destinationdir)
        destinationfile = 'routeros-small-%s.qcow2' % networkidHex
        destinationfile = j.system.fs.joinPaths(destinationdir, destinationfile)
        imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros_template/routeros_template_backup')
        imagefile = j.system.fs.joinPaths(imagedir, 'routeros-small-NETWORK-ID.qcow2')
        xmlsource = j.system.fs.fileGetContents(j.system.fs.joinPaths(imagedir, 'routeros-template.xml'))
        xmlsource = xmlsource.replace('NETWORK-ID', networkidHex)
        j.system.fs.copyFile(imagefile, destinationfile)

        try:
            dom = con.defineXML(xmlsource)
            dom.create()
        except libvirt.libvirtError, e:
            cleanup()
            raise RuntimeError("Could not create VFW vm from template, network id:%s:%s\n%s"%(networkid,networkidHex,e))

        data['internalip'] = internalip

        if not j.system.net.tcpPortConnectionTest(internalip,22):
            print "OK no other router found."
        else:
            raise RuntimeError("IP conflict there is router with %s"%internalip)


        try:
            run = pexpect.spawn("virsh console %s" % name)
            print "Waiting to attach to console"
            run.expect("Connected to domain", timeout=10)
            run.sendline() #first enter to clear welcome message of kvm console
            print 'Waiting for Login'
            run.expect("Login:", timeout=60)
            run.sendline("vscalers")
            run.expect("Password:", timeout=2)
            run.sendline(defaultpasswd)
            print 'waiting for prompt'
            run.expect("\] >", timeout=60) # wait for primpt
            run.send("/ip addr add address=%s/22 interface=internal\r\n" % internalip)
            print 'waiting for end of command'
            run.expect("\] >", timeout=2) # wait for primpt
            run.send("\r\n")
            run.close()
        except Exception,e:
            cleanup()
            raise RuntimeError("Could not set internal ip on VFW, network id:%s:%s\n%s"%(networkid,networkidHex,e)) 

        print "wait max 30 sec on tcp port 22 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip,22,timeout=30):
            print "Router is accessible, initial configuration probably ok."
        else:
            raise RuntimeError("Could not connect to router on %s"%internalip)

        ro=j.clients.routeros.get(internalip,"vscalers",defaultpasswd)
        try:
            ro.ipaddr_remove(DEFAULTGWIP)
            ro.resetMac("internal")
        except Exception,e:
            raise RuntimeError("Could not cleanup VFW temp ip addr, network id:%s:%s\n%s"%(networkid,networkidHex,e)) 

        ro.do("/system/identity/set",{"name":"%s/%s"%(networkid,networkidHex)})
        toremove=[ item for item in ro.list("/") if item.find('.backup')<>-1]
        for item in toremove:
            ro.delfile(item)

        if not "skins" in ro.list("/"):
            ro.mkdir("/skins")
        ro.uploadFilesFromDir("keys")
        ro.uploadFilesFromDir("skins","/skins")
        time.sleep(10)

        ro.executeScript("/ip address remove numbers=[/ip address find network=192.168.1.0]")
        ro.executeScript("/ip address remove numbers=[/ip address find network=192.168.103.0]")
        ro.uploadExecuteScript("basicnetwork")
        ro.ipaddr_set('public', "%s/%s" % (publicip, publiccidr), single=True)

        ipaddr=[]
        for item in ro.ipaddr_getall():
            if item["interface"]=="public":
                ipaddr.append(item["ip"])
        if not ipaddr:
            raise RuntimeError("Each VFW needs to have 1 public ip addr at this state, this vfw has not")

        ro.ipaddr_set('cloudspace-bridge', '192.168.103.1/24',single=True)

        ro.uploadExecuteScript("route", vars={'$gw': publicgwip})
        ro.uploadExecuteScript("ppp")
        ro.uploadExecuteScript("customer")
        ro.uploadExecuteScript("systemscripts")
        cmd="/certificate import file-name=ca.crt passphrase='123456'"
        #ro.executeScript(cmd)
        #import file-name=RB450.crt passphrase="123456"
        #import file-name=RB450.pem passphrase="123456"

        cmd="/user set numbers=[/user find name=admin] password=\"%s\""% password
        ro.executeScript(cmd)

        cmd="/ppp secret remove numbers=[/ppp secret find name=admin]"
        ro.executeScript(cmd)
        cmd="/ppp secret add name=admin service=pptp password=\"%s\" profile=default"%password
        ro.executeScript(cmd)
        cmd="/ip neighbor discovery set [ /interface ethernet find name=public ] discover=no"
        ro.executeScript(cmd)

        print "change port for www"
        ro.executeScript("/ip service set port=9080 numbers=[/ip service find name=www]")
        print "disable telnet"
        ro.executeScript("/ip service disable numbers=[/ip service find name=telnet]")
        print "change port for ftp"
        ro.executeScript("/ip service set port=9021 numbers=[/ip service find name=ftp]")
        print "change port for ssh"
        ro.executeScript("/ip service set port=9022 numbers=[/ip service find name=ssh]")

        print "reboot of router"
        cmd="/system reboot"
        try:
            ro.executeScript(cmd)
        except Exception,e:
            pass
        print "reboot busy"

        start = time.time()
        timeout = 60
        while time.time() - start < timeout:
            try:
                ro=j.clients.routeros.get(internalip,"vscalers",defaultpasswd)
                if ro.ping(publicgwip):
                    print "Failed to ping %s waiting..." % publicgwip
                    break
            except:
                print 'Failed to connect will try again in 3sec'
            time.sleep(3)
        else:
            raise RuntimeError("Could not ping to:%s for VFW %s"%(publicgwip, networkid))

        print "wait max 2 sec on tcp port 9022 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip,9022,timeout=2):
            print "Router is accessible, configuration probably ok."
        else:
            raise RuntimeError("Internal ssh is not accsessible.")

    except:
        cleanup()
        raise

    return data


