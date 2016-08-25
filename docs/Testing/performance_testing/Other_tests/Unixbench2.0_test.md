# Test Case description
- create an account
- create 1 cloudspace for all nodes
- create a vm and run unixbench on it and store its score
- create the number of vms needed to run unixbench on (change it from parameter file)
- When the test is done store the unixbech score of all vm's

## Prerequisite
Have a gener8 run the latest version of openvcloud
Clean the Gener8 so no vm's are running on it.


## Expected result
- Create a result table providing the average unixbench score per vm  
- Result needs to be compared to other similar vm scores in the market
http://serverbear.com/benchmarks/cloud

## Running the Test
- For changing the test parameters: vim Testsuite/2_Unixbench2_test/parameters.cfg 
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory:  jspython Testsuite/2_Unixbench2_test/2_unixbench2.0_test.py 
- After the test has been completed, the test will clean itself.

## Results Sample
- Results can be found in /org_quality/Environment_testing/tests_results/2_unixbench2/(date)_(cpu_name).(env_name)_testresults_(run_number)/
- ex: /org_quality/Environment_testing/tests_results/2_unixbench2/2016-08-18_cpu-01.be-g8-3_testresults_8
- This sample is only for 2 iterations

![unixbench](https://cloud.githubusercontent.com/assets/15011431/14142022/b3a054de-f68b-11e5-8996-259aca0fba93.png)
