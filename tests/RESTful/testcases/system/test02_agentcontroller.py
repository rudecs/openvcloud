import time, random, unittest
from testcases import *
from nose_parameterized import parameterized
from unittest import skip

class AgentController(TestcasesBase):
    def setUp(self):
        pass

    @skip('This test case should be execute manually.')
    def test001_swap_consuming(self):
        """ OVC-011
        #. Get grid nodes info, should succeed.
        #. Choose random cpu node.
        #. Install stress-ng.
        #. Execute ```stress-ng --vm-method rowhammer -r 500```.
        #. Sleep for 10 mins.
        #. Swap alert should be raised.
        #. Kill stress-ng
        """

        self.log.info(' [*] Get gids.')
        response = self.api.system.gridmanager.getNodes()
        self.assertEqual(response.status_code, 200, response.content)
        nodes_data = response.json()

        self.log.info(' [*] Choose random node.')
        cpu_nodes = []
        for data in nodes_data:
            if 'cpu' in data['name']:
                cpu_nodes.append(data)

        cpu_node = random.choice(cpu_nodes)
        node_id = cpu_node['id']
        gid = cpu_node['gid']

        self.log.info(' [*] Install stress-ng for nodeID : %d' % node_id)
        cmd = 'apt-get install -y stress-ng'
        response = self.api.system.agentcontroller.executeJumpscript(gid=gid, cmd=cmd, nid=node_id)
        self.assertEqual(response.status_code, 200, response.content)
        time.sleep(30)

        self.log.info(' [*] Execute ```stress-ng --vm-method rowhammer -r 1024```.')
        cmd = "stress-ng --vm-method rowhammer -r 768 &"
        self.api.system.agentcontroller.executeJumpscript(gid=gid, cmd=cmd, timeout=60, nid=node_id)

        self.log.info(' [*] sleep for 20 mins.')
        for i in range(20):
            print(' [*] sleeping %d ... ' % i)
            time.sleep(60)

        self.log.info(' [*] Get details status.')
        response = self.api.system.health.getDetailedStatus(nid=node_id)
        self.assertEqual(response.status_code, 200, response.content)
        node_status = response.json()
        swap_data = [data for data in node_status['System Load']['data'] if "Swap used value is" in data['msg']][0]
        swap_status = swap_data['status']

        self.log.info(' [*] Check swap value')
        self.assertNotEqual(swap_status, 'OK', swap_data)

    def tearDown(self):
        super().tearDown()
        self.log.info(' [*] Kill stress-ng')
        cmd = "pkill -9 stress-ng"
        response = self.api.system.agentcontroller.executeJumpscript(gid=gid, cmd=cmd, nid=node_id)
        self.assertEqual(response.status_code, 200, response.content)
