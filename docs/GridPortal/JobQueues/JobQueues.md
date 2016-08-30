### Job Queues

On this page you see both the central queue of the agent controller and the queues of the agents.

The first table, which will always only have one line, showing the queues of the agent controller:

![[]](AgentControllerQueues.png)

The second table, having one line per node, shows the queues on the nodes:

![[]](WorkerQueues.png)

There are 4 possible queues:

 * **Default** queue for all kinds of miscellaneous tasks
 * **Hypervisor** queue takes on tasks related to virtual machine management
 * **IO** queue is typically used for backup/restore and long IO bound related work
 * **Process** is for monitoring related jobs only

<br/>In the **Agent Controller Queues** table, there is also a column **Internal**, this is not really a queue, but rather showing the number of internal communications going on between the Agent Controller and worker process on the agents, mostly communication about the queues itself.

Clicking the **Details** link in the last column gets you to the **Job Details** page, showing details of the jobs

![[]](AgentControllerJobs.png)
