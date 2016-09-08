### Private Networks

For each cloud space a virtual private network is automatically created.

Behind the scenes this virtual private network gets its network address from a DHCP server that runs on a separate virtual machine with RouterOS as the operating system, also implementing a firewall that protects all virtual machine on the cloud space for which the RouterOS instance is dedicated.

On the **Private Network** page all private networks are listed:

![[]](PrivateNetworks.png)

For each private network the table shows:
- ID of the private network
- ID of the cloud space for which this private network was created
- Public IP address of the RouterOS dedicated to the private network, shared by all virtual machines of the cloud space
- Private IP address for managing the RouterOS

For more details on a specific private network you click the network **ID**, bringing you to the **Private Network Details** page:

![[]](PrivateNetworkDetails.png)

On the **Private Network Details** page you now also see the ID of the firewall node (**FW Node**) on which the RouterOS (virtual firewall + DHCP server) for this cloud space is running.

Also listed on the **Private Network Details** page are the port forwardings for this cloud space:

![[]](PortForwardings.png)

Here you see the private network (**Destination IP**) addresses assigned by the RouterOS DHCP server that is dedicated to the cloud space.
