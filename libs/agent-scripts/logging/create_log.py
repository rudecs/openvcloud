from JumpScale import j

descr = """
Generate loging files for every account
"""

name = "create_log"
category = "cloudbroker"
organization = "cloudscalers"
async = True
period = 1800  # 0.5 hrs
role = ['master']


def action():
    cbcl = j.clients.portal.getByInstance('cloudbroker')
    loggingactor = cbcl.getActor('cloudapi', 'logs')
    loggingactor.logCloudUnits()
    return True


if __name__ == '__main__':
    action()
