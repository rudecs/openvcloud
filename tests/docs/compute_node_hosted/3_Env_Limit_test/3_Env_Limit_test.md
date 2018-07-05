## Virtual Machines Limit Test

### Prerequisites
- Have a G8 running the latest version of OpenvCloud
- Clean the G8, so no virtual machines are running on it
- Have admin access to one of the physical compute nodes

### Test case description
- Create an account
- Create a cloud space per node
- Create virtual machines (type of the virtual machines need to be selectable in the test parameters) 
- Add one virtual machine at a time and continue this operation until no virtual machine can be added any more

### Expected result
- When no more resources can be added the user should get an 503 error message that states:
`raise exceptions.ServiceUnavailable('Not enough resources available on current location')`

- As soon this error is provided we should have a file created including the following information:

| VM Number | vm name  | CPU's  | Memory | HDD | Node |

### Running the test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing
  ```

- For changing the test parameters:
  ```
  vim functional_testing/Openvcloud/compute_node_hosted/3_Env_Limit_test/parameters.cfg
  ```

- Run the test:
  ```
  jspython functional_testing/Openvcloud/compute_node_hosted/3_Env_Limit_test/3_env_limitation_test.py
  ```

- After the test has been completed, the test will clean itself.

### Result sample
- Results can be found in `/Env_limitation_results/results.table`
- Test output:

![env](https://cloud.githubusercontent.com/assets/15011431/14171111/e85dcee6-f739-11e5-86ea-8537bd7187f5.png)
