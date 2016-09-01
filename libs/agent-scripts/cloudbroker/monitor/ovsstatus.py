from JumpScale import j
descr = """
Checks every defined period if all OVS processes still run

Shows WARNING if process not running anymore

"""

organization = 'cloudscalers'
author = "khamisr@codescalers.com"
version = "1.0"
category = "monitor.healthcheck"
roles = ['storagenode']
period = 60 # 1min
enable = True
async = True
queue = 'process'
log = True

def action():
    ovsresults = list()
    ovscmds = {'OK': 'initctl list | grep ovs | grep start/running | sort',
               'HALTED': 'initctl list | grep ovs | grep -v start/running | sort'}
    for state, cmd in ovscmds.items():
        exitcode, results = j.system.process.execute(cmd, outputToStdout=True)
        if exitcode == 0:
            for result in results.splitlines():
                msg = result.split(' ')[0]
                ovsresults.append({'message': msg, 'uid': msg, 'category': 'OVS Services', 'state': state})
                if state != 'OK':
                    msg += "is in state %s" % state
                    j.errorconditionhandler.raiseOperationalCritical(msg, 'monitoring', die=False)
        else:
            ovsresults.append({'message': '', 'category': 'OVS Services', 'state': 'UNKNOWN'})

    return ovsresults


if __name__ == '__main__':
    print action()
