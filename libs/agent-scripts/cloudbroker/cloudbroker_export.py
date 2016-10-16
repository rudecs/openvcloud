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
    from CloudscalerLibcloud import openvstorage
    from CloudscalerLibcloud.utils import webdav
    import tempfile
    tmpdir = tempfile.mkdtemp()
    try:
        ovfpath = '%s/ovf' % tmpdir
        j.system.fs.createDir(ovfpath)
        j.system.fs.writeFile('%s/descriptor.ovf' % ovfpath, envelope)
        tmptar = '%s/res.tar.gz' % tmpdir
        tmpvolname = '%s/disk-%%i.vmdk' % ovfpath
        for i, disk in enumerate(disks):
            print("Exporting to", tmpvolname % i)
            openvstorage.exportVolume(disk, tmpvolname % i)
        print('compressing')
        j.system.fs.targzCompress(ovfpath, tmptar, gzipped=False)
        print('finished compressing')
        webdav.upload_file(link, username, passwd, path, tmptar)
    finally:
        j.system.fs.removeDirTree(tmpdir)

if __name__ == "__main__":
    from CloudscalerLibcloud.utils import ovf
    a = ovf.model_to_ovf({'name': u'mie', 'mem': 512, 'disks': [{'name': 'disk-0.vmdk', 'size': 10737418240}], 'cpus': 1, 'osname': u'Ubuntu 16.04 x64', 'os': u'ubuntu', 'description': u'mie'})
    print(action('http://192.168.57.201/owncloud/remote.php/webdav', 'myuser', 'rooter', '/images/mie.tar.gz', """<?xml version="1.0"?>
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
</Envelope>""", [u'openvstorage+tcp://192.168.57.231:26203/vm-98/bootdisk-vm-98']))
