from multiprocessing import cpu_count
import libvirt
from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
from JumpScale import j


class Dispatcher(object):

    OVERSUPSCRIPTION = 4

    def __init__(self):
        self.phy_count = cpu_count()
        self.host_count = self.get_cpu_host_count()
        self.cpus = {i: CPU(i) for i in range(self.host_count, self.phy_count)}
        self.quarantine_prio = [i for i in reversed(range(self.host_count, self.phy_count))]
        self.connection = LibvirtUtil()
        self.init_quarantine()

    @classmethod
    def get_cpu_host_count(cls):
        count = cpu_count()
        if count <= 16:
            return 1
        elif count <= 32:
            return 2
        else:
            return 4

    @classmethod
    def get_cpu_virsh_num(cls):
        return cpu_count() - cls.get_cpu_host_count()

    @staticmethod
    def is_quarantined(vmid):
        _, out = j.system.process.execute('virsh vcpupin "%s" --live' % (vmid), ignoreErrorOutput=True)
        vals = [map(lambda y: y.strip(), x.split(':')) for x in out.split('\n')[2:] if x]
        if not vals or '-' in vals[0][1]:
            return False
        return True

    @staticmethod
    def get_quarantined_vm_pins(vmid):
        _, out = j.system.process.execute('virsh vcpupin "%s" --live' % (vmid), ignoreErrorOutput=True)
        vals = [map(lambda y: y.strip(), x.split(':')) for x in out.split('\n')[2:] if x]
        if not Dispatcher.is_quarantined(vmid):
            return {}
        else:
            return {int(i): int(j) for i, j in vals}

    def init_quarantine(self):
        for domain in self.connection.list_domains():
            if domain['state'] == libvirt.VIR_DOMAIN_RUNNING:
                vmid = domain['id']
                pins = Dispatcher.get_quarantined_vm_pins(domain['id'])
                for vcpu, pcpu in pins.items():
                    self.cpus[pcpu].incr(vmid)

    def alloc(self, vmid, vcpus):
        cpus = '%s-%s' % (self.host_count, self.phy_count - 1)
        return {i: cpus for i in range(vcpus)}

    def dealloc(self, vmid):
        self.defrag()

    def defrag(self):
        pass

    def alloc_quarantine(self, vmid, vcpus):
        # TODO: locking should be done here
        results = []
        req = vcpus
        for i in self.quarantine_prio:
            cpu = self.cpus[i]
            avail = Dispatcher.OVERSUPSCRIPTION - cpu.curr
            if avail > 0:
                results.append((cpu, avail))
                req -= avail
            if req <= 0:
                # in case that we now have extra cpus
                if req < 0:
                    results[-1] = (results[-1][0], results[-1][1] + req)
                break
        else:
            raise RuntimeError("Don't have enough cpu for the required vcpus")

        res = {}
        i = 0
        for cpu, avail in results:
            cpu.alloc(vmid, avail)
            for _ in range(avail):
                res[i] = str(cpu.index)
                i += 1
        return res

    def dealloc_quarantine(self, vmid):
        removed = []
        for i in self.quarantine_prio:
            cpu = self.cpus[i]
            res = cpu.dealloc(vmid)
            if res:
                removed.append(i)
        self.defrag_quarantine()

    def defrag_quarantine(self):
        i = 0
        j = len(self.quarantine_prio) - 1
        while i < j:
            to = self.cpus[self.quarantine_prio[i]]
            from_ = self.cpus[self.quarantine_prio[j]]
            avail = Dispatcher.OVERSUPSCRIPTION - to.curr
            present = from_.curr
            if not avail:
                i += 1
                continue
            if not present:
                j -= 1
                continue
            to_move = min(avail, present)
            for vmid, count in from_.vms.items():
                to_move_vm = min(to_move, count)
                from_.incr(vmid, -to_move_vm)
                to.incr(vmid, to_move_vm)
                to_move -= to_move_vm
                Dispatcher.move_cpus(vmid, to_move_vm, from_.index, to.index)
                if to_move == 0:
                    break

    def quarantine_vm(self, vmid):
        if not Dispatcher.is_quarantined(vmid):
            vm = self.connection._get_domain(vmid)
            if vm is None:
                raise RuntimeError("cannot get the machine with id %s" % (vmid))
            vcpus = vm.vcpusFlags()
            self.dealloc(vmid)
            cpus = self.alloc_quarantine(vmid, vcpus)
            Dispatcher.set_cpu(vm.UUIDString(), cpus)

    def unquarantine_vm(self, vmid):
        if Dispatcher.is_quarantined(vmid):
            vm = self.connection._get_domain(vmid)
            if vm is None:
                raise RuntimeError("cannot get the machine with id %s" % (vmid))
            vcpus = vm.vcpusFlags()
            self.dealloc_quarantine(vmid)
            cpus = self.alloc(vmid, vcpus)
            Dispatcher.set_cpu(vm.UUIDString(), cpus)

    @staticmethod
    def set_cpu(vmid, pcpus):
        for i in pcpus:
            j.system.process.execute("virsh vcpupin %s --vcpu '%d' --cpulist '%s' --live" % (vmid, i, pcpus[i]), ignoreErrorOutput=True)

    @staticmethod
    def move_cpus(vmid, count, from_, to):
        pins = Dispatcher.get_quarantined_vm_pins(vmid)
        for i, k in pins.items():
            if k == from_:
                count -= 1
                j.system.process.execute("virsh vcpupin %s --vcpu '%d' --cpulist '%s' --live" % (vmid, i, to), ignoreErrorOutput=True)
                if count == 0:
                    return
        raise RuntimeError("cannot move this number of vcores")


class CPU(object):
    def __init__(self, index):
        self.index = index
        self.curr = 0
        self.vms = {}

    def alloc(self, vmid, vcpus):
        curr = self.vms.get(vmid, 0)
        self.vms[vmid] = vcpus
        self.curr += vcpus - curr
        return bool(vcpus - curr)

    def dealloc(self, vmid):
        if vmid in self.vms:
            self.curr -= self.vms[vmid]
            self.vms.pop(vmid)
            return True
        return False

    def incr(self, vmid, vcpus=1):
        curr = self.vms.get(vmid, 0)
        self.alloc(vmid, curr + vcpus)
        if self.vms[vmid] == 0:
            self.dealloc(vmid)
        return bool(vcpus)
