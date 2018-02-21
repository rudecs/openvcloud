from JumpScale import j


descr = """
Deletes link used to report previous update.
"""

organization = "greenitglobe"
author = "chaddada@greenitglobe.com"
license = "bsd"
version = "1.0"
category = "cloudbroker"
timeout = 30
order = 1
async = True


def action(path):
    j.system.fs.remove(path)

if __name__ == '__main__':
    action()
