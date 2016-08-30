#!/usr/bin/env python2.7
import fcntl
import os
import os.path
import subprocess
import sys
import syslog
import time
import libvirt
import re
from string import Template
from xml.etree import ElementTree

# Some defaults
command_name = sys.argv[0]
vsctl = "/usr/bin/ovs-vsctl"
ofctl = "/usr/bin/ovs-ofctl"
ip = "/sbin/ip"
publicbr="{{envid}}"
flowtemplate='/etc/libvirt/hooks/flowtemplate'

# no flowtable? no party! (but let VM start anyway)
if not os.path.isfile(flowtemplate):
    send_to_syslog("No flow template, exiting")
    sys.exit(0)

def send_to_syslog(msg):
    pid = os.getpid()
    syslog.syslog("%s[%d] - %s" %(command_name, pid, msg))

def ip_link_set(device, args):
    doexec([ip, "link", "set",  device, args])

""" Hmmm this is here (blatantly copied) for locking concurrency on ovs_ofctl stuff. not sure if needed, we'll see """
def acquire_lock(path):
    lock_file = open(path, 'w')
    while True:
        send_to_syslog("attempting to acquire lock %s" % path)
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            send_to_syslog("acquired lock %s" % path)
            return lock_file
        except IOError, e:
            send_to_syslog("failed to acquire lock %s because '%s' - waiting 1 second" % (path, e))
            time.sleep(1)
# From BBI (BigBadInternet) Luv it!
def doexec(args):
        """Execute a subprocess, then return its return code, stdout and stderr"""
        send_to_syslog(args)
        proc = subprocess.Popen(args,stdin=None,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True)
        rc = proc.wait()
        stdout = proc.stdout
        stderr = proc.stderr
        return (rc, stdout, stderr)

""" Unusable function: Calling libvirt from within libvirt causes deadlock"""
def get_dom_ifaces_libvirt(dom):
  tree=ElementTree.fromstring(dom.XMLDesc(0))
  devices={}
  for interface in tree.findall("devices/interface"):
      target=interface.find("target")
      mac=interface.find("mac")
      dev=target.get("dev")
      macaddr=mac.get("address")
      if not devices.has_key(dev):
          devices[dev] = macaddr
  return devices

def list_ports_in_of():
    ports = []
    ipm=re.compile('(?<=in_port\=)\d{1,5}')
    cmd = ofctl + " dump-flows " + publicbr
    (r,s,e) = doexec(cmd.split())
    li=[line.strip() for line in s.readlines() if 'in_port' in line]
    ports = [int(ipm.search(x).group(0)) for x in li]
    return ports

def cleanup_flows(bridge_name):
    # flows of which ports do not exist any more get removed (generic cleanup)
    flowports = list_ports_in_of()
    activeports = [int(get_vswitch_port(x)) for x in list_ports(publicbr)]
    ap = set(activeports)
    todelete = [x for x in flowports if x not in ap]
    for i in todelete:
        clear_vswitch_rules(bridge_name, i)

def get_all_ifaces_ls():
    netpath = '/sys/class/net' ; ifaces = {}
    for i in os.listdir(netpath):
        with open(os.path.join(netpath,i,"address")) as f:
            addr = f.readline().strip()
            ifaces[i] = addr
    return ifaces

def get_attached_mac_port(virt_vif):
    if virt_vif:
        cmd = vsctl + ' -f table -d bare --no-heading -- --columns=ofport,external_ids list Interface ' + virt_vif
        (r,s,e) = doexec(cmd.split())
        o = s.readline().split()
        port = o.pop(0)
        mac = o.pop(0).split('=')[1]
        return port,mac
    else:
        send_to_syslog("No matching virt port found in get_attached_mac_port(virt_vif): ; qemu hook bails")
        sys.exit(0)


def get_dom_ifaces(guest):
    devs = get_all_ifaces_ls()
    devices = {}
    for vif,  mac in devs.items():
        if re.search(guest,  vif):
            devices[vif] = mac
    return devices


def get_bridge_name(vif_name):
    (rc, stdout, stderr) = doexec([vsctl, "port-to-br", vif_name])
    return stdout.readline().strip()

def get_pub_vifname(domifaces):
    #dict received [ vif: mac ]
    for vif_name in domifaces.keys():
        if get_bridge_name(vif_name) == publicbr:
            # returns vif
            return vif_name
        else:
            send_to_syslog("No interface of guest is connected on %s, or bridge doesn't exist!" % publicbr)

def list_ports(bridge_name):
    (rc, stdout, stderr) = doexec([vsctl, "list-ports", bridge_name])
    ports = [line.strip() for line in stdout.readlines()]
    return ports

def get_vswitch_port(vif_name):
    (rc, stdout, stderr) = doexec([vsctl, "get", "interface", vif_name, "ofport"])
    return stdout.readline().strip()

def clear_vswitch_rules(bridge_name, port):
    doexec([ofctl, "del-flows", bridge_name, "in_port=%s" % port])

def add_flow(bridge_name, args):
    doexec([ofctl, "add-flow", bridge_name, args])

def get_rules(file):
    with open(file) as f:
        li=[line.strip() for line in f.readlines() if not '#' in line]
    return li


def create_vswitch_rules(bridge_name, port, mac):
    for rule in get_rules(flowtemplate):
        ft = Template(rule)
        f = ft.substitute({'port': port, 'mac': mac })
        add_flow(bridge_name,f)

def wrap_get_port(guest):
    (port,mac) = get_attached_mac_port(get_pub_vifname(get_dom_ifaces(guest)))
    return port,mac

"""
No Jumpscale here to keep python script as lean and mean as possible
"""

if __name__ == "__main__":
    if len(sys.argv) != 5:
        # something fishy calling us, let's NOT stop and start the domain anyway. YMMV, if you wish.
        send_to_syslog("Qemu Hook script called with  erroneous number of arguments %s , Will not exit with an error " % sys.argv)
        sys.exit(0)
    else:
        guest, stage = sys.argv[1:3]
        send_to_syslog("Called with Guest=%s, Stage: %s" %   (guest, stage))
        # Aight, we need three stages , 'started' , 'stopped' and 'reconnect'
        if stage =='started' :
            # vm is started, as of now booting, quickly add flows
            pub_vif_port, pub_vif_mac = wrap_get_port(guest)
            create_vswitch_rules(publicbr, pub_vif_port, pub_vif_mac)
        elif stage == 'release':
            # remove rules for port
            cleanup_flows(publicbr)
        elif stage == 'reconnect':
            # Libvirtd has been restarted, we get called for every running vm -> expensive?
            pub_vif_port, pub_vif_mac = wrap_get_port(guest)
            # these overwrite the flows
            create_vswitch_rules(publicbr, pub_vif_port, pub_vif_mac)
            # cleanup lingering flows, while we're at it
            cleanup_flows(publicbr)
        else:
            send_to_syslog("/etc/libvirt/hooks/qemu called without known state %s %s" % (guest, stage))
            sys.exit(0)
# vim: tabstop=4 expandtab sw=4 softtabstop=4
