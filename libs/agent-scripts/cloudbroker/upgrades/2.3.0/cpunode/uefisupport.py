from JumpScale import j

descr = """
Upgrade script
* Will add ovmf package needed to boot uefi based vms

"""

category = "libvirt"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['cpunode']
async = True


def action():
    j.system.platform.ubuntu.install('ovmf')

if __name__ == '__main__':
    print(action())
