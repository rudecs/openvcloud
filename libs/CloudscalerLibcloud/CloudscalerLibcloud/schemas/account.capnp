@0x934efea7f327fff3;

using CloudSpace = import "cloudspace.capnp".CloudSpace;

struct Account {
  accountId @0  :UInt32;
  cloudspaces @1 :List(CloudSpace);
}
