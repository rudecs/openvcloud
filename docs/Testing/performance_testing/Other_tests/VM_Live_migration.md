# Test Case description
- Create an account
- Create a cloudspace
- Create a vm (type of vm need to be selectable in the test parameters)
- Do a random read write action of files on that vm.
- During the read/write actions,  move that vm to another CPU node with force option "no"

## Prerequisite
- Have a gener8 run the latest version of openvcloud.
- Have admin rights as a user

## Expected result
- vm should be installed on another CPU node
- Approximately no downtime should be experienced.
- vm should not have data loss.

- PASS: When above is ok then the test 
- FAIL: When one of the above actions is not satisfied


## Running the Test
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory:  jspython Testsuite/6_vm_live_migration_test/6_vm_live_migration_test.py 
- After the test has been completed, the test will clean itself.

## Result Sample
![livem](https://cloud.githubusercontent.com/assets/15011431/16177906/76a13782-3642-11e6-9986-209a8c807f5d.png)
