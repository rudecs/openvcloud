from JumpScale import j

descr = """
Upgrade script
Will remove unneeded Grafana Dashboards.
"""

category = "libvirt"
organization = "greenitglobe"
author = "chaddada@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True

def action():

    def check_roles(node_roles):
        stat_roles = ['controller', 'cpunode', 'storagenode']
        for role in node_roles:
            if role in stat_roles:
                return True
        return False

    def delete_dashboard(name):
        grafclient = j.clients.grafana.getByInstance('main')
        dashboards = grafclient.listDashBoards()
        for dashboard in dashboards:
            if dashboard.get('title') and name in dashboard.get('title'):
                grafclient.delete(dashboard)
    
    scl = j.clients.osis.getNamespace('system')
    nodes = scl.node.search({})[1:]
    delete_dashboard('jsagent8')
    for node in nodes:
        if not check_roles(node['roles']):
            delete_dashboard(node['name'])

if __name__ == '__main__':
    print(action())