# New performance stress testing Specifications
## Purpose
The purpose of this test is to check the performance of our Gener8 system comparing to similar solutions in the market.


## Overall description of the test
### Prerequisites
Prior to starting the test we should have a clean environment. No vm's should be installed on the physical nodes.

Main focus should be testing on the specified hardware for the G8’s.  Thus only performed on G8-S / G8-M and G8-F system.   Other systems in the test environment can be ok for functional testing, but will not deliver performance measurements that are representable of systems sold to customers.

We have 3 separate aims for the performance test  
1 - measure the boundaries of a G8 in different configurations  
2 - compare the performance versus other competitive systems based on objective benchmarks  
3 - understand when the system brakes

### Goal of the test  
The expected outcome of the tests is  

1 - that we can measure key benchmark scores with a system under load for typical workloads  
2 - we understand how the system performance of a VM degrades while adding more load  
3 - we understand the impact of load on the time it takes to create new machines  

### Benchmarks te be executed (to be done)

Benchmarks that need to be executed for this release are 
1 - Unixbench : with Benchmarks tested on AWS and Google Cloud
2 - IOZone : with Benchmarks tested on AWS and Google Cloud
3 - (for a later stage) Filebench

### Expected graphs (to be done)

#### Time to create VM graph
Aim of the graph is to show how Time to create VM regresses when more load is pushed on the machine - ideally we should continue to test until time becomes unacceptably high (e.g. > 5 minutes)
- 2D graph
- Vertical axis - time to create VM (from API call to delivery of SSH key to requestor)
- Horizontal axis 1 - load - measured in amount of logical CPU’s deliver in all nodes in G8
- Horizontal axis 2 - load - measured in total amount of memory used in all nodes in G8

#### Overall UnixBench performance over load
Aim of the graph is to show how performance of one VM degrades if you add more load to the system - ideally we should continue to test until the machine’s UnixBench benchmark drops below 75% of the initial benchmark
- 2D graph
- Shows overall UnixBench performance of the first VM created in the test iteration
- Horizontal axis 1 - load - measured in amount of logical CPU’s deliver in all nodes in G8
- Horizontal axis 2 - load - measured in total amount of memory used in all nodes in G8

#### Overall UnixBench performance versus industrial benchmark
Benchmarks to be drawn from actual tests on similar VMs on AWS and Google Cloud

We assume 50% loaded G8 (so create VM’s with different loads until 50% of CPU, 50% of Mem and 50% of DISKs are used in a G8) - do this with all types of VM a G8 can deliver such that we have UnixBench performance benchmarks on this loaded system for all different machines.

- Graph = a table that compares the G8 VM Unixbench versus Unixbench with similar configured VM on AWS and Google Cloud

#### Overall IOZone performance over load

- 2D graph
- Vertical access in IOPS
- Horizontal access in amount of disks created 
- Datapoints - 3 lines that give the IOPS = f(amount of disks) with different IOZone parameters (always Random R/W, 1 graph with large record and large filesize, one with small records and large filesize, one with small record and small filesize)

