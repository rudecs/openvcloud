@0x934efea7f327fff0;
struct CloudSpace {
  cloudSpaceId @0 :UInt32;
  accountId @1 :UInt32;
  machines @2 :List(VMachine);
  state @3 :Text;
  imageName @4 :Text;
  struct VMachine {
    id @0 :UInt32;
    disksSize @1 :Float32;
    memSize @2 :Float32;
    cpuSize @3 :Float32;
    pubIps @4 :Int8;
    network @5 :Network;
    iops_read @6 :Float32
    iops_write @7 :Float32

    struct Network {
      rx @0 :Float32;
      tx @1 :Float32;
    }
  }
}
