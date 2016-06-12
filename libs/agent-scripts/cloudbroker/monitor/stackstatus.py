from JumpScale import j
descr = """
check status of stack
"""

organization = 'cloudscalers'
author = "deboeckj@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['cpunode']
period = 60 * 5 # 30min
timeout = 60 * 1
enable = True
async = True
queue = 'io'
log = True

def action():
    ccl = j.clients.osis.getNamespace('cloudbroker')
    stacks = ccl.stack.search({'referenceId': str(j.application.whoAmI.nid), 'gid': j.application.whoAmI.gid})[1:]
    category = 'Stack Status'
    if not stacks:
        return [{'message': 'Node with role CPUNode is not configured as stack',
                 'uid': 'Node with role CPUNode is not configured as stack',
                 'category': category,
                 'state': 'ERROR'}
                ]
    stack = stacks[0]
    if stack['status'] == 'ERROR':
        return [{'message': 'Node is in error status',
                 'uid': 'Node is in error status',
                 'category': category,
                 'state': 'ERROR'}
                ]
    elif stack['status'] == 'ENABLED':
        return [{'message': 'Node is enabled',
                 'category': category,
                 'state': 'OK'}
                ]
    elif stack['status'] in ['MAINTENANCE', 'DECOMISSIONED']:
        return [{'message': 'Node state is %' % stack['status'],
                 'uid': 'Node state is %' % stack['status'],
                 'category': category,
                 'state': 'SKIPPED'}
                ]
    else:
        return [{'message': 'Node has an invalid state %' % stack['status'],
                 'uid': 'Node has an invalid state %' % stack['status'],
                 'category': category,
                 'state': 'ERROR'}
                ]

if __name__ == '__main__':
    print action()
