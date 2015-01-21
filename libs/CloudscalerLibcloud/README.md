This is a extension to the libcloud libvirt support.
Normally extensions are directly written in libcloud but this is ver specific toward cloudscalers-cloudbroker.

Configuration and setup:

* Put CloudscalerLibcloud somewhere in your python path
* Copy your public ssh rsa key towards all the nodes you wan't to connect. E.g put them in every .ssh/authorized_keys file.


Usages:

from CloudscalerLibcloud.compute.drivers.libvirt_driver import CSLibvirtNodeDriver

conn = CSLibvirtNodeDirver(uri='qemu+ssh://nodeip/system')

#if you don't specify a specific backend the dummy broker backend will be used to list a set of sizes and images.

You can specify the backend with:

from CloudscalerLibcloud.utils.connection import CloudBrokerConnection

or for the dummy backend

from CloudscalerLibcloud.utils.connection import DummyConnection

cb = CloudBrokerConnection(cloudbrokerportalclient)

Set the the cloudbroker on the libvirt libcloud connection:

conn.set_backend(cb)


Other important files:

/templates contains the specific libvirt basic templates



