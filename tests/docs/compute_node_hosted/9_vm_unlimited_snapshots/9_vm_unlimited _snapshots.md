## Snapshots Limit Test

### Prerequisites
- Have a G8 running the latest version of OpenvCloud
- Clean the G8, so no virtual machines are running on it
- Have admin access to one of the physical compute nodes

### Test case description
- Create a virtual machine in a cloud space 
- Create a new text file on any directory on the new virtual machine
- Take a snapshot for this VM
- Repeat above 2 steps depending on the the number of snapshots need to be created
- Stop the virtual machine
- Revert to the latest_snapshot -1
- Start the virtual machine

### Expected behavior
- Data of the latest snapshot -1 should be on the virtual machine
- All later snapshots than the one selected should be removed from the portal...

### Running the Test
- Go to the `G8_testing` directory:
  ```bash
  cd G8_testing 
  ```

- Run the test:  
  ```
  jspython functional_testing/Openvcloud/compute_node_hosted/9_vm_unlimited_snapshots/9_vm_snapshots_test.py 6
  ```
-  '**6**' is the number of snapshots to be created
- Any number of snapshots can be specified to figure out the maximum number of snapshots that can be created of a virtual machine
- After the test has been completed, the test will clean itself
