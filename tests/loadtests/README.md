
## LoadTests

### purpose

* Create virtualmachines remotely and benchmark their storage capabilities
* Benchmark results may be suitable for jenkins [plot plugin](https://wiki.jenkins-ci.org/display/JENKINS/Plot+Plugin)
* If user chose more than one machines with the same package/size, then results of those machines will be averaged

### Benchmarking Linux machines
* We use [UnixBench](https://github.com/kdlucas/byte-unixbench) tool
  * The tool runs tests twice [once on single CPU and another across all available CPUs/parallel]
  * We care about the final Index Score result(s) of that tool
  * WARNING: this tool takes too much to run especially on machines with 1 CPU (20M-30M)
  * output of this tool may look like snippet below:
```
Dhrystone 2 using register variables       35090941.4 lps   (10.0 s, 7 samples)
Double-Precision Whetstone                     4500.8 MWIPS (9.6 s, 7 samples)
Execl Throughput                               4018.9 lps   (30.0 s, 2 samples)
File Copy 1024 bufsize 2000 maxblocks        584367.0 KBps  (30.0 s, 2 samples)
File Copy 256 bufsize 500 maxblocks          151641.4 KBps  (30.0 s, 2 samples)
File Copy 4096 bufsize 8000 maxblocks       1774469.7 KBps  (30.0 s, 2 samples)
Pipe Throughput                              773041.0 lps   (10.0 s, 7 samples)
Pipe-based Context Switching                 218082.7 lps   (10.0 s, 7 samples)
Process Creation                              11256.3 lps   (30.0 s, 2 samples)
Shell Scripts (1 concurrent)                   7870.4 lpm   (60.0 s, 2 samples)
Shell Scripts (8 concurrent)                   1027.4 lpm   (60.0 s, 2 samples)
System Call Overhead                         560719.0 lps   (10.0 s, 7 samples)
System Benchmarks Index Values               BASELINE       RESULT    INDEX
Dhrystone 2 using register variables         116700.0   35090941.4   3006.9
Double-Precision Whetstone                       55.0       4500.8    818.3
Execl Throughput                                 43.0       4018.9    934.6
File Copy 1024 bufsize 2000 maxblocks          3960.0     584367.0   1475.7
File Copy 256 bufsize 500 maxblocks            1655.0     151641.4    916.3
File Copy 4096 bufsize 8000 maxblocks          5800.0    1774469.7   3059.4
Pipe Throughput                               12440.0     773041.0    621.4
Pipe-based Context Switching                   4000.0     218082.7    545.2
Process Creation                                126.0      11256.3    893.4
Shell Scripts (1 concurrent)                     42.4       7870.4   1856.2
Shell Scripts (8 concurrent)                      6.0       1027.4   1712.3
System Call Overhead                          15000.0     560719.0    373.8
                                                                   ========
System Benchmarks Index Score                                        1107.9```

### Benchmarking Linux machines
* To be continued


### Setup
* Install dependencies using : ```sudo sh setup.sh```

### Run
* We have 2 versions of the loadtest scripts that can be run differently
 * loadtests.py   (working/tested)  but not so hot code
   * Run using ```python  loadtests.py numberOfWindowsMachines numberOfLinuxMachines```
 * fabfile.py  (working) better code using fabric API & more OOP code
   * Run using ```fab test:linux_count=2,windows_count=2,cloudspacename=lenoire1```
   * All parameters are optional and you can safely ommit some of them
   * The script can take cloudspacenames ```[lenoire1, demo1]``` if ommitted then default is ```demo1```
 * both scripts sleeps for about 30M before attempting to collect statistics from remote virtual machines

### Results
* One CSV file with Only one record/row result
* For each size/package selected we get only one file with the index score of benchmarking for linux machines
* Examples on file names
 * ubuntu.512G_1CPU.csv
 * windows.512G_1CPU.csv
* Examples on the contents of the files
 * If package has only 1 CPU:
 
```One Single Run
2822```
 * If package has more than 1 CPU:

```One Single Run,'Parallel Runs across all cores
2822,2790``` 
