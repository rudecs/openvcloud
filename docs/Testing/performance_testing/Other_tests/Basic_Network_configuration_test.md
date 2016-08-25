# Test Case description

- Create a user, an account  and a crossponding cloudspace 
- create a vm on each available node in the cloudspace
- create port forwarding on all vm's and check public access --> All vm's should be accessible by public network over ssh
- write a file from public to the created vm's in the cloudspace using scp --> File should be transferred having no data loss
- write a file from all available vm's to all the other vm's in the same cloudspace. --> File should be transferred having no data loss

## Expected result
- PASS: All files should be completely available on all vm's
- FAIL: If there is too much latency or if vm fails to send or receive data.

## Running the Test
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory: jspython Testsuite/1_Network_config_test/1_Network_conf_test.py
- After the test has been completed, the test will clean itself.

## Result sample
![netconf](https://cloud.githubusercontent.com/assets/15011431/16178107/84e9af3a-3648-11e6-916e-ee4e03baa8b7.png)

