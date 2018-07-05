## Network Configuration Test

### Prerequisites
- Have a G8 running the latest version of OpenvCloud
- Clean the G8, so no virtual machines are running on it
- Have admin access to one of the physical compute nodes

### Test case description
- Create an account
- Create a user
- Create a cloud space

> Check public network connectivity of the cloud space, the cloud space should have a public IP address.

- Create a virtual machine on each available node in the cloud space
- Create port forwarding on all virtual machines and check public access

> All virtual machines should be accessible on the public network over SSH.

- Write a file from public network to the created virtual machines in the cloud space using the `scp`command.

> File should be transferred having no data loss.

- Write a file from all available virtual machines to all the other virtual machines in the same cloud space.

> File should be transferred having no data loss.

### Expected result
PASS: All files should be completely available on all virtual machines. A test succeed message is presented.  
FAIL: If there is too much latency, if virtual machines fails to send or receive data...

### Running the test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing
  ```

- From inside that directory:
  ```bash
  jspython functional_testing/Openvcloud/compute_node_hosted/1_Network_config_test/1_Network_conf_test.py 
  ```

- After the test has completed, the test will clean itself.

### Result sample
![netconf](https://cloud.githubusercontent.com/assets/15011431/16178107/84e9af3a-3648-11e6-916e-ee4e03baa8b7.png)
