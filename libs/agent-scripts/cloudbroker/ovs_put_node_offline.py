from JumpScale import j  # NOQA

descr = """
Put node offline on ovs
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
async = True


def action(storageip):
    import sys
    sys.path.append('/opt/OpenvStorage')
    from ovs.dal.lists.pmachinelist import PMachineList
    from ovs.extensions.storageserver.storagedriver import StorageDriverClient
    pm = PMachineList.get_by_ip(storageip)
    sr = pm.storagerouters[0]
    sd = sr.storagedrivers[0]
    sdc = StorageDriverClient.load(sd.vpool)
    sdc.mark_node_offline(str(sd.storagedriver_id))
    return True
