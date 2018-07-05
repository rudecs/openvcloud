## Cloud Spaces Limit Test

### Prerequisites
- Have a G8 run the latest version of OpenvCloud
- Have admin access to one of the physical compute nodes

### Test case description
- Create an account
- Create a cloud space
- Create a virtual machine with minimum specs on the new cloud space
- Create another cloud space
- Create a new virtual machine with minimum specs on the new cloud space
- Repeat above iterations until the system provides a message stating that there are no more resources available to deploy a new cloud space

### Expected result
A file should be created with all created cloud spaces. 

> The number of created cloud spaces should be equal to the number of free public IP addresses.  

### Running the test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing 
  ```

- Run the test:  
  ```
  jspython functional_testing/Openvcloud/compute_node_hosted/5_cloudspace_limits_test/5_cs_limits_test.py
  ```

- After the test has been completed, the test will clean itself

### Result sample
@todo
