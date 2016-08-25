# Test description:

- Create a vm in a cloudspace 
- create a text file in the any directory on the vm
- Take a snapshot 
- Repeat the above 2 steps for certain number of snapshots
- Stop the vm 
- If n snapshots have been taken, rollback to the n-1 snapshot.  
- Start vm


## Expected behavior
- Data of the latest n-1 snapshot (n-1 written files) should be on the vm 
- All later snapshots than the one selected should be removed from the portal...

## Running the Test
- Go to performance testing directory: cd org_quality/Environment testing/performance testing
- From inside that directory:  jspython Testsuite/9_vm_unlimited_snapshots/9_vm_snapshots_test.py **6**
    -  '**6**' is the number of snapshots to be created
- Any number of snapshots can be provided to figure out the max number of snapshots that can be created for VM.
- After the test has been completed, the test will clean itself.
