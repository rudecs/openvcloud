## Components

![](https://docs.google.com/drawings/d/e/2PACX-1vQ1VSIuIXgAWT3W2mx-GR79_BAj0ST5-DhNHt8TuK-Ji1lWhsUh3GaYXYbj7oHu372vEzwlvUJWLsku/pub?w=706&h=645)

[edit image](https://docs.google.com/drawings/d/1G0kzg5FEMheZwc8cRUZi5QP5NEkfXzr5HXvkPsXNcsk/edit)

In what follows all components are discussed bottom-up.


### System Abstraction Layer

The **System Abstraction Layer** (SAL) is a thin abstraction layer making it easy for developers to interact with all system components at the level of a server node.

For more details check the [SAL documentation in the GitBook covering JumpScale 8 Core](https://gig.gitbooks.io/jumpscale-core8/content/SAL/SAL.html).


### Node

In this context a node is a server node typically running the Ubuntu OS or - in the most recent G8 installations - the G8-OS.


### Agent

On each server node an **Agent** is responsible for executing jobs received from the **Agent Controller**. These jobs are actually **JumpScripts**, which are Python scripts interacting with the system through the **System Abstraction Layer**.

Logs, errors and statistics collected by the **Agent**  from the running **JumpScripts** are fed back to the **Agent Controller**.


### Master

Each single-location or multi-location OpenvCloud environment is managed from a **Master**. This is a collection of virtual machines or Docker containers running in the **Master Cloud Space** on a remote location, physically separated from OpenvCloud server nodes it orchestrates.

For more details about the **Master Cloud Space** and how to access it see the [How to Connect to an OpenvCloud Environment](../Sysadmin/Connect/connect.md) section.


### Agent Controller

The **Agent Controller** acts as a job controller distributing work to the **Agents**.

Since server nodes are not publicly accessible all communication between the **Agents** and the **Agent Controller** happens through HTTP Long Polling initiated by the agents.


### Datacenter Abstraction Layer

Also implemted by JumpScale 8 Core components is the **Datacenter Abstraction Layer** providing developers an interface to interact with the **Agent Controller**, and thus the server nodes.


### Master REST API

Both local and remote interactions with the **Datacenter Abstraction Layer** happens through REST API.


### Operator Portal

Operators administer their OpenvCloud environment through the Operator Portal, which are actually the [Cloud Broker Portal](../CloudBrokerPortal/CloudBrokerPortal.md) and the [Grid Portal](../GridPortal/GridPortal.md).

The portals are created using the **JumpScale Portal Framework** that features wiki pages that interact with the REST APIs through macros.


### End User Portal

End users have access through the **End User Portal**, which is another portal created using the **JumpScale Portal Framework**.

### OpenvCloud API

The OpenvCloud API permits thirdparty tools like [Terraform](https://www.terraform.io/) to make provisioning of VM's automatic and repeatable, so that the raw compute and storage capacity can be consumed in a very easy and tested procedure.
Using the API customized portals for end customers can be built as well, as any functionality for creating and managing VM's and cloudspaces is available via the OpenvCloud API.