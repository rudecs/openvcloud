# Test Case description
- create an account
- create a cloudspace per node
- create vm's (type of vm's need to be selectable in the test parameters) 
- Add one vm at a time and continue this operation untill no vm's can be added any more.

## Prerequisite
- Have a gener8 run the latest version of openvcloud
- Clean the Gener8 so no vm's are running on it.

## Expected result
- when no more resources can be added the user should get an 503 error message that states:
raise exceptions.ServiceUnavailable('Not enough resources available on current location')
- As soon this error is provided we should have a file created including the following information


## Running the Test
- For changing the test parameters: vim Testsuite/3_Env_Limit_test/parameters.cfg 
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory:   jspython Testsuite/3_Env_Limit_test/3_env_limitation_test.py 
- After the test has been completed, the test will clean itself.

## Results Sample
- Results can be found in /org_quality/Environment_testing/tests_results/3_env_limitation/(date)_(cpu_name).(env_name)_testresults_(run_number)/
- ex: /org_quality/Environment_testing/tests_results/3_env_limitation/2016-08-18_cpu-01.be-g8-3_testresults_8

![env](https://cloud.githubusercontent.com/assets/15011431/14171111/e85dcee6-f739-11e5-86ea-8537bd7187f5.png)
