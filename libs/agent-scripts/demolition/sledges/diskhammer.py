from JumpScale import j

descr = """
Simulate a disk failure.
"""

category = "demolition.sledgehammer"
organization = "greenitglobe"
author = "rob@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = []
async = True
queue = 'process'


def action(device):
    with open(device,'w') as f:
        # write 4Mb of 0's to the disk
        f.write('\0' * 1024 * 1024 * 4)
        f.flush()

if __name__ == '__main__':
    action('/dev/null')
