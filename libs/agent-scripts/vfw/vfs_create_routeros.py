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
docleanup = True


def cleanup(name, networkid):
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
    import jinja2
    import time
    import os
    acl = j.clients.agentcontroller.get()
    edgeip, edgeport, edgetransport = acl.execute('greenitglobe', 'getedgeconnection', role='storagedriver', gid=j.application.whoAmI.gid)


    hrd = j.atyourservice.get(name='vfwnode', instance='main').hrd
    DEFAULTGWIP = hrd.get("instance.vfw.default.ip")
    netrange = hrd.get("instance.vfw.netrange.internal")
    defaultpasswd = hrd.get("instance.vfw.admin.passwd")
    username = hrd.get("instance.vfw.admin.login")
    newpassword = hrd.get("instance.vfw.admin.newpasswd")
    destinationfile = None

    def destroy_device(path):
        acl.execute('cloudscalers', 'destroyvolume',
                    role='storagedriver', gid=j.application.whoAmI.gid,
                    args={'path': path})

    data = {'nid': j.application.whoAmI.nid,
            'gid': j.application.whoAmI.gid,
            'username': username,
            'password': newpassword
            }

    networkidHex = '%04x' % int(networkid)
    internalip = str(netaddr.IPAddress(netaddr.IPNetwork(netrange).first + int(networkid)))
    name = 'routeros_%s' % networkidHex

    j.clients.redisworker.execFunction(cleanup, _queue='hypervisor', name=name,
                                       networkid=networkid)
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

        devicename = 'routeros/{0}/routeros-small-{0}'.format(networkidHex)
        destinationfile = 'openvstorage+%s://%s:%s/%s' % (
            edgetransport, edgeip, edgeport, devicename
        )
        destroy_device(destinationfile)
        imagedir = j.system.fs.joinPaths(j.dirs.baseDir, 'apps/routeros/template/')
        imagefile = j.system.fs.joinPaths(imagedir, 'routeros-small-NETWORK-ID.qcow2')
        xmltemplate = jinja2.Template(j.system.fs.fileGetContents(j.system.fs.joinPaths(imagedir, 'routeros-template.xml')))
        print 'Converting image %s -> %s' % (imagefile, destinationfile)
        j.system.platform.qemu_img.convert(imagefile, 'qcow2', destinationfile.replace('://', ':'), 'raw')

        xmlsource = xmltemplate.render(networkid=networkidHex, name=devicename,
                                       edgehost=edgeip, edgeport=edgeport,
                                       edgetransport=edgetransport)

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
            run.send("/quit\r\n")
            run.expect("Login:", timeout=2)
            run.close()
        except Exception, e:
            raise RuntimeError("Could not set internal ip on VFW, network id:%s:%s\n%s"%(networkid,networkidHex,e))

        print "wait max 30 sec on tcp port 22 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip, 9022,timeout=30):
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
        ro.executeScript('/file remove numbers=[/file find]')

        if not "skins" in ro.list("/"):
            ro.mkdir("/skins")

        # create certificates
        certdir = j.system.fs.getTmpDirPath()
        j.tools.sslSigning.create_self_signed_ca_cert(certdir)
        j.tools.sslSigning.createSignedCert(certdir, 'server')

        ro.uploadFilesFromDir(certdir)
        vpnpassword = j.tools.hash.sha1(j.system.fs.joinPaths(certdir, 'ca.crt'))
        j.system.fs.removeDirTree(certdir)
        ro.uploadFilesFromDir("skins","/skins")

        pubip = "%s/%s" % (publicip, publiccidr)
        privateip = "192.168.103.1/24"
        ro.uploadExecuteScript("basicnetwork", vars={'$pubip': pubip, '$privateip': privateip})
        ro.uploadExecuteScript("route", vars={'$gw': publicgwip})
        ro.uploadExecuteScript("certificates")
        ro.uploadExecuteScript("ppp", vars={'$vpnpassword': vpnpassword})
        ro.uploadExecuteScript("systemscripts")
        ro.uploadExecuteScript("services")

        print "change admin password"
        try:
            ro.executeScript('/user set %s password=%s' % (username, newpassword))
        except:
            pass

        ro = j.clients.routeros.get(internalip,username,newpassword)
        if not ro.arping(publicgwip, 'public'):
            raise RuntimeError("Could not ping to:%s for VFW %s"%(publicgwip, networkid))

        start = time.time()
        timeout = 60
        while time.time() - start < timeout:
            try:
                ro.uploadExecuteScript("customer", vars={'$password': password})
                break
            except Exception as e:
                print 'Failed to set skin will try again in 1sec', e
            time.sleep(1)
        else:
            raise RuntimeError("Failed to set customer skin")

        print "wait max 2 sec on tcp port 9022 connection to '%s'"%internalip
        if j.system.net.waitConnectionTest(internalip,9022,timeout=2):
            print "Router is accessible, configuration probably ok."
        else:
            raise RuntimeError("Internal ssh is not accsessible.")

        print 'Finished configuring VFW'

    except:
        if docleanup:
            j.clients.redisworker.execFunction(cleanup, _queue='hypervisor', name=name,
                                               networkid=networkid)
            if destinationfile:
                destroy_device(destinationfile)
        raise

    return data


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--networkid', type=int, required=True)
    parser.add_argument('-p', '--public-ip', dest='publicip', required=True)
    parser.add_argument('-pg', '--public-gw', dest='publicgw', required=True)
    parser.add_argument('-pc', '--public-cidr', dest='publiccidr', required=True, type=int)
    parser.add_argument('-pw', '--password', required=True)
    parser.add_argument('-c', '--cleanup', action='store_true', default=False, help='Cleanup in case of failure')
    options = parser.parse_args()
    docleanup = options.cleanup
    action(options.networkid, options.publicip, options.publicgw, options.publiccidr, options.password)
