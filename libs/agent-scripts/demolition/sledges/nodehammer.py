from JumpScale import j

descr = """
Simulate a node failure, an immediate shutdown is issued without clean shutdown of daemons or filesystems.
"""

category = "demolition.sledgehammer"
organization = "greenitglobe"
author = "rob@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'process'


def action():
    with open('/proc/sys/kernel/sysrq','w') as f:
        f.write('1')
    with open('/proc/sysrq-trigger','w') as f:
        f.write('o')

if __name__ == '__main__':
    result = action()
    print result
