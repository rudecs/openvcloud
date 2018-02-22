from JumpScale import j

descr = """
Upgrade script
Migrate node status
"""

category = "libvirt"
organization = "greenitglobe"
author = "foudaa@greenitglobe.com"
license = "bsd"
version = "2.0"
roles = ['master']
async = True

def action():
    ccl = j.clients.osis.getNamespace('cloudbroker')
    ocl = j.clients.osis.getNamespace('system')
    nodes_ids = ocl.node.list()
    for node_id in nodes_ids:
        node = ocl.node.get(node_id)
        if not node.status:
            stack = ccl.stack.get(node.id)
            stack = ccl.stack.searchOne({'referenceId': str(node.id)})
            if stack:
                node.status = stack['status']
            else:
                node.status = 'ENABLED'
        ocl.node.set(node)

if __name__ == '__main__':
    action()
