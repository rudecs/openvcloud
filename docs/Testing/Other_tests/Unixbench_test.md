# Test Case description
- create an account
- create 2 cloudspaces per node
- create 7 vm's per cloudspace, so 14 vms per node
- Install unixbench on 2 vm's per cloudspace (4x Unixbench per node)
- Start unixbench with a random time interval on all vm's (make sure you test all cores
- Run this Unixbench test on the vms that unixbench has been installed on for a variable amount of iterations 

## Prerequisite
Have a gener8 run the latest version of openvcloud
Clean the Gener8 so no vm's are running on it.

## Expected result
- Create a result table providing the average unixbench score per vm  
- Result needs to be compared to other similar vm scores in the market
  http://serverbear.com/benchmarks/cloud

## Running the Test
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory:  jspython  Testsuite/4_Unixbench_test/4_Unixbench_test.py 
- After the test has been completed, the test will clean itself.

## Result Sample
- Results can be found in  /org_quality/Environment_testing/tests_results/4_unixbench1/(date)(cpu_name).(env_name)_testresults(run_number)/
ex: /org_quality/Environment_testing/tests_results/4_unixbench1/2016-08-18_cpu-01.be-g8-3_testresults_8

- Test output (for 2 iterations)

![4unixbench](https://cloud.githubusercontent.com/assets/15011431/14319591/6de39fe8-fc1a-11e5-8f7e-aa41378273ce.png)

