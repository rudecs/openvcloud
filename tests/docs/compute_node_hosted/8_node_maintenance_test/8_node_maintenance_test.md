## Node Maintenance Test

### Prerequisites
- Have a G8 running the latest version of OpenvCloud
- Clean the G8, so no virtual machines are running on it
- Have admin access to one of the physical compute nodes

### Test case description
- Create an account
- Create a cloud space
- Create a virtual machine on a node x (type of virtual machine needs to be selectable in the test parameters) 
- Do a random read write action of files on that virtual machine
- During the read/write action, put node x in Maintenance with option "move VMs"

### Expected result
- Virtual machine on that node should be moved to another CPU node
- Virtual machine should approximately experience no downtime
- Virtual machine shouldn't have data loss

### Run the test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing 
  ```
  
- Run the test:
  ```
  jspython functional_testing/Openvcloud/compute_node_hosted/8_node_maintenance_test/8_node_maintenance_test.py
  ```

- After the test has been completed, the test will clean itself
