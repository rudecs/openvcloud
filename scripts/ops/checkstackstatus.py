from JumpScale import j
import prettytable
import sys


sys.path.append('/opt/code/github/0-complexity/openvcloud/apps/cloudbroker')
j.db.serializers.getSerializerType('j')


class MaskClass(object):
    def __init__(self, *args, **kwargs):
        pass


class StackInfo(object):
    def __init__(self):
        self.ccl = j.clients.osis.getNamespace('cloudbroker')
        from cloudbrokerlib import cloudbroker
        cloudbroker.models = self.ccl
        cloudbroker.CloudSpace = MaskClass
        j.apps = MaskClass()
        j.apps.system = MaskClass()
        j.apps.system.contentmanager = MaskClass()
        j.apps.system.contentmanager.getActors = lambda *a: ['libloud_libvirt']
        self.rcb = cloudbroker.CloudBroker()

    def get_stack_info(self):
        stacks = []
        for location in self.ccl.location.search({})[1:]:
            stacks.extend(self.rcb.getCapacityInfo(location['gid']))
        return stacks

    def print_stack_info(self, stacks=None):
        if stacks is None:
            stacks = self.get_stack_info()
        table = prettytable.PrettyTable(['Name', 'VM Count', 'ROS Count', 'Memory'])
        for stack in stacks:
            meminfo = "{:.2f} + {} / {:.2f} GiB".format(stack['usedmemory']/1024., stack['reservedmemory']/1024, stack['totalmemory']/1024.)
            table.add_row([stack['name'], stack['usedvms'], stack['usedros'], meminfo])
        print str(table)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    stackinfo = StackInfo()
    stackinfo.print_stack_info()


