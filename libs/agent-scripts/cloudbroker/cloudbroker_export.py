from JumpScale import j

descr = """
Follow up creation of export
"""

name = "cloudbroker_export"
category = "cloudbroker"
organization = "greenitglobe"
author = "elawadim@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
queue = 'io'
async = True
timeout = 60 * 60


def action(link, username, passwd, path, envelope, disks):
    from io import BytesIO
    import tarfile
    import subprocess
    from CloudscalerLibcloud import openvstorage

    envelope = j.tools.text.toStr(envelope)
    try:
        pr = subprocess.Popen(['curl', '%s/%s' % (link.rstrip('/'), path.lstrip('/')), '--user', '%s:%s' % (username, passwd), '--upload-file', '-'], stdin=subprocess.PIPE)
        with tarfile.open(mode='w|', fileobj=pr.stdin) as tf:
            ti = tarfile.TarInfo('descriptor.ovf')
            ti.size = len(envelope)
            tf.addfile(ti, BytesIO(envelope))
            with openvstorage.TempStorage() as ts:
                tmpvolname = 'disk-%i.vmdk'
                for i, disk in enumerate(disks):
                    openvstorage.exportVolume(disk, '%s/disk.vmdk' % ts.path)
                    tf.add(name='%s/disk.vmdk' % ts.path, arcname=tmpvolname % i)
                    j.system.fs.remove('%s/disk.vmdk' % ts.path)

    finally:
        pr.communicate()


if __name__ == "__main__":
    print(action('http://192.168.27.152/owncloud/remote.php/webdav', 'myuser', 'rooter', '/images/mie.tar.gz', """<?xml version="1.0"?>
    <Envelope ovf:version="2.0" xml:lang="en-US"
     xmlns="http://schemas.dmtf.org/ovf/envelope/2"
     xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/2"
     xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData.xsd"
     xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData.xsd"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:epasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_EthernetPortAllocationSettingData.xsd"
     xmlns:sasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_StorageAllocationSettingData.xsd">

      <References>
        <File ovf:href="disk-0.vmdk" ovf:id="file0"/>
      </References>


      <DiskSection>
        <Info>List of the virtual disks used in the package</Info>
        <Disk ovf:capacity="107374182400" ovf:diskId="vmdisk0" ovf:fileRef="file0"/>
      </DiskSection>

      <NetworkSection>
        <Info>Logical networks used in the package</Info>
        <Network ovf:name="NAT">
          <Description>Logical network used by this appliance.</Description>
        </Network>
      </NetworkSection>
      <VirtualSystem ovf:id="ubuntu">
        <Name>owncloudr</Name>
        <Info>rgerg</Info>
        <OperatingSystemSection ovf:id="94">
          <Info>The kind of installed guest operating system</Info>
          <Description>Ubuntu 14.04 x64</Description>
        </OperatingSystemSection>
        <VirtualHardwareSection>
          <Info>Virtual hardware requirements for a virtual machine</Info>
          <System>
            <vssd:ElementName>Virtual Hardware Family</vssd:ElementName>
            <vssd:InstanceID>0</vssd:InstanceID>
            <vssd:VirtualSystemIdentifier>ubuntu</vssd:VirtualSystemIdentifier>
            <vssd:VirtualSystemType>kvm</vssd:VirtualSystemType>
          </System>
          <Item>
            <rasd:Caption>1 virtual CPU</rasd:Caption>
            <rasd:Description>Number of virtual CPUs</rasd:Description>
            <rasd:InstanceID>1</rasd:InstanceID>
            <rasd:ResourceType>3</rasd:ResourceType>
            <rasd:VirtualQuantity>2</rasd:VirtualQuantity>
          </Item>
          <Item>
            <rasd:AllocationUnits>MegaBytes</rasd:AllocationUnits>
            <rasd:Caption>512 MB of memory</rasd:Caption>
            <rasd:Description>Memory Size</rasd:Description>
            <rasd:InstanceID>2</rasd:InstanceID>
            <rasd:ResourceType>4</rasd:ResourceType>
            <rasd:VirtualQuantity>2048</rasd:VirtualQuantity>
          </Item>
          <Item>
            <rasd:Address>0</rasd:Address>
            <rasd:Caption>ideController0</rasd:Caption>
            <rasd:Description>IDE Controller</rasd:Description>
            <rasd:InstanceID>3</rasd:InstanceID>
            <rasd:ResourceSubType>PIIX4</rasd:ResourceSubType>
            <rasd:ResourceType>5</rasd:ResourceType>
          </Item>
          <Item>
            <rasd:Address>1</rasd:Address>
            <rasd:Caption>ideController1</rasd:Caption>
            <rasd:Description>IDE Controller</rasd:Description>
            <rasd:InstanceID>4</rasd:InstanceID>7
            <rasd:ResourceSubType>PIIX4</rasd:ResourceSubType>
            <rasd:ResourceType>5</rasd:ResourceType>
          </Item>
          <Item>
            <rasd:Address>0</rasd:Address>
            <rasd:Caption>sataController0</rasd:Caption>
            <rasd:Description>SATA Controller</rasd:Description>
            <rasd:InstanceID>5</rasd:InstanceID>
            <rasd:ResourceSubType>AHCI</rasd:ResourceSubType>
            <rasd:ResourceType>20</rasd:ResourceType>
          </Item>
          <Item>
            <rasd:Address>0</rasd:Address>
            <rasd:Caption>usb</rasd:Caption>
            <rasd:Description>USB Controller</rasd:Description>
            <rasd:InstanceID>6</rasd:InstanceID>
            <rasd:ResourceType>23</rasd:ResourceType>
          </Item>
          <Item>
            <rasd:AddressOnParent>3</rasd:AddressOnParent>
            <rasd:AutomaticAllocation>false</rasd:AutomaticAllocation>
            <rasd:Caption>sound</rasd:Caption>
            <rasd:Description>Sound Card</rasd:Description>
            <rasd:InstanceID>7</rasd:InstanceID>
            <rasd:ResourceSubType>ensoniq1371</rasd:ResourceSubType>
            <rasd:ResourceType>35</rasd:ResourceType>
          </Item>
          <EthernetPortItem>
            <epasd:AutomaticAllocation>true</epasd:AutomaticAllocation>
            <epasd:Caption>Ethernet adapter on 'NAT'</epasd:Caption>
            <epasd:Connection>NAT</epasd:Connection>
            <epasd:InstanceID>10</epasd:InstanceID>
            <epasd:ResourceSubType>E1000</epasd:ResourceSubType>
            <epasd:ResourceType>8</epasd:ResourceType>
          </EthernetPortItem>

          <StorageItem>
            <sasd:AddressOnParent>0</sasd:AddressOnParent>
            <sasd:Caption>disk1</sasd:Caption>
            <sasd:Description>Disk Image</sasd:Description>
            <sasd:HostResource>/disk/vmdisk0</sasd:HostResource>
            <sasd:InstanceID>9</sasd:InstanceID>
            <sasd:Parent>5</sasd:Parent>
            <sasd:ResourceType>17</sasd:ResourceType>
          </StorageItem>

        </VirtualHardwareSection>
      </VirtualSystem>
    </Envelope>""", [u'openvstorage+tcp://10.112.1.14:26203/vm-2272/bootdisk-vm-2272']))
