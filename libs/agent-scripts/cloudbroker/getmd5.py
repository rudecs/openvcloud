from JumpScale import j

descr = """
Get md5sum of file
"""

category = "cloudbroker"
organization = "cloudscalers"
author = "deboeckj@codescalers.com"
license = "bsd"
version = "1.0"
queue = "io"
async = True

def action(filepath):
    return j.system.fs.md5sum(filepath)
