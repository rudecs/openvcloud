## VM Live Migration Test

### Prerequisites
- Have a G8 run the latest version of OpenvCloud
- Have admin access to one of the physical compute nodes

### Test case description
- Create an account
- Create a cloud space
- Create a virtual machine (type of virtual machine need to be selectable in the test parameters)
- Do a random read write action of files on that virtual machine
- During the read/write action , move the vm to another CPU node with option "force_option=no"

### Expected result
- Virtual machine should be moved to another CPU node
- Virtual machine should have experienced approximately no downtime
- Virtual machine should not have data loss  

When above is OK then the test is PASS
When one of the above actions failed then it's a FAIL

### Running the test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing 
  ```

- Run the rest:  
  ```
  jspython functional_testing/Openvcloud/compute_node_hosted/6_vm_live_migration_test/6_vm_live_migration_test.py 
  ```

- After the test has been completed, the test will clean itself.

### Result sample

![livem](https://cloud.githubusercontent.com/assets/15011431/16177906/76a13782-3642-11e6-9986-209a8c807f5d.png)
