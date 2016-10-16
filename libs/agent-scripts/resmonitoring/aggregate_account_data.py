from JumpScale import j
import os
import re
import tarfile
import cStringIO
import capnp


descr = """
gather statistics about OVS backends
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "account.monitoring"
period = 60 * 60  # everyhour
timeout = period * 0.2
order = 1
enable = True
async = True
queue = 'process'
log = False

roles = ['master']


def action(gid=None):
    """
    Send tar of account data on  each enviroment
    """
    agentcontroller = j.clients.agentcontroller.get()
    cbcl = j.clients.osis.getNamespace("cloudbroker")
    data = list()
    jobs = list()
    results = list()

    capnp.remove_import_hook()
    Cloudspace_capnp = capnp.load('cloudspace.capnp')
    Account_capnp = capnp.load('Account.capnp')

    # schedule command
    for location in cbcl.location.search({})[1:]:
        jobs.append(agentcontroller.scheduleCmd(cmdcategory="greenitglobe",
                                                cmdname="collect_account_data",
                                                nid=None,
                                                gid=location["gid"],
                                                wait=True))

    # get return from each job.
    for job in jobs:
        result = agentcontroller.waitJumpscript(job=job)
        accounts = dict()

        # read the tar.
        c = cStringIO.StringIO()
        c.write(result['result'])
        c.seek(0)
        tar = tarfile.open(mode="r", fileobj=c)
        members = tar.getmembers()
        for member in members:
            if member.name.endswith(".bin"):
                accountid, year, month, day, hour = re.findall(
                    "opt/var/resourcetracking/active/([\d]+)/([\d]+)/([\d]+)/([\d]+)/([\d]+)/", member.name)[0]
                if accountid in accounts:
                    if "%s/%s/%s/%s" % (year, month, day, hour) not in accounts[accountid]:
                        accounts[accountid] = {"%s/%s/%s/%s" % (year, month, day, hour): [member]}
                    else:
                        accounts[accountid]["%s/%s/%s/%s" % (year, month, day, hour)].append(member)

                else:
                    accounts[accountid] = {"%s/%s/%s/%s" % (year, month, day, hour): member}

        for account_id, dates in accounts.iteritems():
            account = Account_capnp.new_message()

            for i, val in enumerate(dates.iteritems()):
                date, member = val
                if member.name.endwith("bin"):
                    year, month, day, hour = re.findall(
                        "([\d]+)/([\d]+)/([\d]+)/([\d]+)/([\d]+)/", date)[0]
                    account.accountId = account_id
                    cloudspaces = account.init("cloudspaces", len(members))

                    # read the capnp file obj.
                    fd = cStringIO.StringIO()
                    binary_content = tar.extractfile(member).read()
                    fd.write(binary_content)
                    fd.seek(0)
                    cloudspace_obj = Cloudspace_capnp.read(fd)
                    cloudspaces[i] = cloudspace_obj
                    fd.close()
                    with open('/opt/var/resourcetracking/%s account_capnp.bin' % os.path.join(account_id,
                                                                                              year,
                                                                                              month,
                                                                                              day,
                                                                                              hour), 'w+b') as f:
                        account.write(f)
        c.close()

if __name__ == '__main__':
    print(action())
