
## Test Case description
- create an account and corresponding cloudspace.
- create a vm on a node x (type of vm need to be selectable in the test parameters)
- Do a random read write action of files on that vm.
- During the read/write actions, put node x in maintenance (with option move VMs)

## Prerequisite
- Have a gener8 run the latest version of openvcloud.
- Have admin rights as a user

## Expected result
- vm should be installed on another CPU node
- Approximately no downtime should be experienced
- vm shouldn't have data loss  

- When above is ok then the test is PASS
- When one of the above actions fail then its a FAIL

## Running the Test
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory: jspython Testsuite/8_node_maintenance_test/8_node_maintenance_test.py 
- After the test has been completed, the test will clean itself.
