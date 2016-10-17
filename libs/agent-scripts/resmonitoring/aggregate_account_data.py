from JumpScale import j
import os
import re
import tarfile
import io
import base64


descr = """
gather statistics about OVS backends
"""

organization = "greenitglobe"
author = "tareka@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "account.monitoring"
period = "30 * * * *"
timeout = 120
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
    import CloudscalerLibcloud
    import capnp
    agentcontroller = j.clients.agentcontroller.get()
    cbcl = j.clients.osis.getNamespace("cloudbroker")
    jobs = list()

    capnp.remove_import_hook()
    schemapath = os.path.join(os.path.dirname(CloudscalerLibcloud.__file__), 'schemas')
    resources_capnp = capnp.load(os.path.join(schemapath, 'resourcemonitoring.capnp'))

    # schedule command
    for location in cbcl.location.search({})[1:]:
        jobs.append(agentcontroller.scheduleCmd(cmdcategory="greenitglobe",
                                                cmdname="collect_account_data",
                                                nid=None,
                                                roles=['controller'],
                                                gid=location["gid"],
                                                wait=True))

    # get return from each job.
    accounts = dict()
    for job in jobs:
        result = agentcontroller.waitJumpscript(job=job)

        # read the tar.
        c = io.BytesIO()
        if result['state'] == 'ERROR':
            raise RuntimeError("%s\n%s" % (result['result']['errormessage'], result['result']['errormessage']))
        result_decoded = base64.decodestring(result['result'])
        c.write(result_decoded)
        c.seek(0)
        tar = tarfile.open(mode="r", fileobj=c)
        members = tar.getmembers()
        for member in members:
            if member.name.endswith(".bin"):
                accountid, year, month, day, hour = re.findall(
                    "opt/jumpscale7/var/resourcetracking/active/([\d]+)/([\d]+)/([\d]+)/([\d]+)/([\d]+)/", member.name)[0]

                datekey = (year, month, day, hour)
                accounts.setdefault(accountid, {datekey: []}).setdefault(datekey, []).append(member)


    for account_id, dates in accounts.iteritems():

        for date, members in dates.iteritems():
            account = resources_capnp.Account.new_message()
            year, month, day, hour = date
            account.accountId = int(account_id)
            cloudspaces = account.init("cloudspaces", len(members))

            for i, member in enumerate(members):
                # read the capnp file obj.
                binary_content = tar.extractfile(member).read()
                cloudspace_obj = resources_capnp.CloudSpace.from_bytes(binary_content)
                cloudspaces[i] = cloudspace_obj
                filepath = '/opt/jumpscale7/var/resourcetracking/%s/' % os.path.join(account_id,
                                                                                     year,
                                                                                     month,
                                                                                     day,
                                                                                     hour)
                try:
                    os.makedirs(filepath)
                except OSError as err:
                    if err.errno != 17:
                        raise

            with open(os.path.join(filepath, "account_capnp.bin"), 'w+b') as f:
                account.write(f)

if __name__ == '__main__':
    print(action())
