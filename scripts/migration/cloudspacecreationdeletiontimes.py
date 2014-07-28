#!/usr/bin/env python
import sys, time
from JumpScale import j
from JumpScale.baselib.cmdutils import ArgumentParser

def migrate():
    import JumpScale.grid.osis
    ccl = j.core.osis.getClientForNamespace('cloudbroker')
    cloudspaces = ccl.cloudspace.simpleSearch({'location': whereami})
    for spaced in cloudspaces:
        if spaced['status'] != 'DESTROYED':
            space = ccl.cloudspace.get(spaced['id'])
            space.creationTime = int(time.time())
            ccl.cloudspace.set(space)


if __name__ == '__main__':
    j.application.start('migrator')
    parser = ArgumentParser(description='set creation and deletiontimes of cloudspaces')
    options = parser.parse_args()
    migrate()
    j.application.stop(0)
