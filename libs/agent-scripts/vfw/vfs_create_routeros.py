from JumpScale import j

descr = """
create and start a routeros image
"""

organization = "jumpscale"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
category = "deploy.routeros"
enable = True
async = True
queue = 'default'


def cleanup(name, networkid, destinationdir):
    import libvirt
    from CloudscalerLibcloud.utils import libvirtutil
    con = libvirt.open()
    try:
        dom = con.lookupByName(name)
        if dom.isActive():
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
        libvirtutil.LibvirtUtil().cleanupNetwork(networkid)
    except:
        pass


def createVM(xml):
    import libvirt
    con = libvirt.open()
    dom = con.defineXML(xml)
    dom.create()


def createNetwork(xml):
    import libvirt
    con = libvirt.open()
    private = con.networkDefineXML(xml)
    private.create()
    private.setAutostart(True)

def action(networkid, publicip, publicgwip, publiccidr, password):
    import pexpect
    import netaddr
    import time
    import os

    hrd = j.atyourservice.get(name='vfwnode', instance='main').hrd
    DEFAULTGWIP = hrd.get("instance.vfw.default.ip")
    netrange = hrd.get("instance.vfw.netrange.internal")
    defaultpasswd = hrd.get("instance.vfw.admin.passwd")
    username = hrd.get("instance.vfw.admin.login")
    newpassword = hrd.get("instance.vfw.admin.newpasswd")

    data = {'nid': j.application.whoAmI.nid,
            'gid': j.application.whoAmI.gid,
            'username': username,
            'password': newpassword
            }

    networkidHex = '%04x' % int(networkid)
    internalip = str(netaddr.IPAddress(netaddr.IPNetwork(netrange).first + int(networkid)))
    networkname = "space_%s" % networkidHex
    name = 'routeros_%s' % networkidHex
    destinationdir = '/mnt/vmstor/routeros/%s' % networkidHex

    j.clients.redisworker.execFunction(cleanup, _queue='hypervisor', name=name,
                                       networkid=networkid, destinationdir=destinationdir)
    print 'Testing network'
    if not j.system.net.tcpPortConnectionTest(internalip, 22, 1):
        print "OK no other router found."
    else:
        raise RuntimeError("IP conflict there is router with %s"%internalip)

    try:
        # setup network vxlan
        print 'Creating network'
        createnetwork = j.clients.redisworker.getJumpscriptFromName('cloudscalers', 'createnetwork')
        j.clients.redisworker.execJumpscript(jumpscript=createnetwork, _queue='hypervisor', networkid=networkid)

        j.system.fs.createDir(destinationdir)
        destinationfile = 'routeros-small-%s.raw' % networkidHex
        destinationfile = j.system.fs.joinPaths(destinationdir, destinationfile)
        imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros/template/')
        imagefile = j.system.fs.joinPaths(imagedir, 'routeros-small-NETWORK-ID.qcow2')
        xmlsource = j.system.fs.fileGetContents(j.system.fs.joinPaths(imagedir, 'routeros-template.xml'))
        xmlsource = xmlsource.replace('NETWORK-ID', networkidHex)
        print 'Converting image'
        j.system.platform.qemu_img.convert(imagefile, 'qcow2', destinationfile, 'raw')
        size = int(j.system.platform.qemu_img.info(destinationfile)['virtual size'] * 1024)
        fd = os.open(destinationfile, os.O_RDWR|os.O_CREAT)
        os.ftruncate(fd, size)
        os.close(fd)

        print 'Starting VM'
        try:
            j.clients.redisworker.execFunction(createVM, _queue='hypervisor', xml=xmlsource)
        except Exception, e:
            raise RuntimeError("Could not create VFW vm from template, network id:%s:%s\n%s"%(networkid,networkidHex,e))

        data['internalip'] = internalip

        try:
            run = pexpect.spawn("virsh console %s" % name)
            print "Waiting to attach to console"
            run.expect("Connected to domain", timeout=10)
            run.sendline() #first enter to clear welcome message of kvm console
            print 'Waiting for Login'
            run.expect("Login:", timeout=60)
            run.sendline(username)
            run.expect("Password:", timeout=2)
            run.sendline(defaultpasswd)
            print 'waiting for prompt'
            run.expect("\] >", timeout=60) # wait for primpt
            run.send("/ip addr add address=%s/22 interface=internal\r\n" % internalip)
            print 'waiting for end of command'
            run.expect("\] >", timeout=2) # wait for primpt
            run.send("\r\n")
            run.close()
        except Exception, e:
            raise RuntimeError("Could not set internal ip on VFW, network id:%s:%s\n%s"%(networkid,networkidHex,e))

        print "wait max 30 sec on tcp port 22 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip,22,timeout=30):
            print "Router is accessible, initial configuration probably ok."
        else:
            raise RuntimeError("Could not connect to router on %s"%internalip)

        ro=j.clients.routeros.get(internalip,username,defaultpasswd)
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
        print "change admin password"
        try:
            ro.executeScript('/user set %s password=%s' % (username, newpassword))
        except:
            pass

        ro=j.clients.routeros.get(internalip,username,newpassword)

        print "reboot of router"
        cmd="/system reboot"
        try:
            ro.executeScript(cmd)
        except Exception:
            pass
        print "reboot busy"

        print "wait max 60 sec on tcp port 9022 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip,9022,timeout=60):
            print "Router is accessible, configuration probably ok."
        else:
            raise RuntimeError("Internal ssh is not accsessible.")

    except:
        j.clients.redisworker.execFunction(cleanup, _queue='hypervisor', name=name,
                                           networkid=networkid, destinationdir=destinationdir)
        raise

    return data


