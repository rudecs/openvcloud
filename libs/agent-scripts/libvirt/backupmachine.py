from JumpScale import j

descr = """
Script to upload backups
"""

name = "backupmachine"
category = "libvirt"
organization = "greenitglobe"
author = "hendrik@awingu.com"
license = "bsd"
version = "1.0"
roles = []
queue = "io"
async = True


def action(machineid,backupname,location,emailaddress):
    from CloudscalerLibcloud.utils.libvirtutil import LibvirtUtil
    from xml.etree import ElementTree
    import os
    import libvirt
    import time
    from email.mime.text import MIMEText
    import smtplib

    libvirtconn = libvirt.openReadOnly()
    pool = libvirtconn.storagePoolLookupByName("VMStor")
    poolvolumes = pool.listVolumes()
    connection = LibvirtUtil()
    root_disks = []
    to_upload = []
    domain = libvirtconn.lookupByUUIDString(machineid)
    disks = connection._get_domain_disk_file_names(domain)
    print 'ROOTDISKS %s' % str(disks)
    for disk in disks:
        name, ext = os.path.splitext(disk)
        if ext == '.qcow2':
            root_disks.append(disk)

    def get_dependency_disk(diskpath):
        if os.path.basename(diskpath) not in poolvolumes:
    	    return None
        volume = libvirtconn.storageVolLookupByPath(diskpath)
        if not volume:
            return None
        diskxml = ElementTree.fromstring(volume.XMLDesc(0))
        xmlbacking = diskxml.find('backingStore/path')
        if xmlbacking.text:
            backendfile = xmlbacking.text
        else:
            backendfile = None
        return backendfile

    def send_mail(body, subject, sender, receiver):
        msg = MIMEText(body, 'html')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver
        server = '	'
        smtp = None
        try:
            smtp = smtplib.SMTP(server, timeout=5)
            smtp.sendmail(sender, receivers, msg.as_string())
        finally:
            if smtp:
                smtp.quit()
        return True

    
    for disk in root_disks:
        backendfile = disk
        to_upload.append(backendfile)
        while backendfile:
    	    backendfile = get_dependency_disk(backendfile)
    	    if backendfile:	
    		    to_upload.append(backendfile)

    #start uploading files to location
    timestamp = time.time()
    locations = 'Backup Locations: \n'
    try:
        for upload in to_upload:
    	    source = 'file://%s' % upload
    	    destination_file = os.path.basename(upload)
    	    destination = '%s/%s/%s' % (location, backupname, destination_file)
    	    locations = locations + destination + '\n'
    	    j.cloud.system.fs.copyFile(source, destination)
       	destination_xml = '%s/%s/machine.xml' % (location, backupname)
        local_source_xml = '/tmp/%s_%s' % (backupname, timestamp)
        domainxml = domain.XMLDesc(0)
        j.system.fs.writeFile(local_source_xml, domainxml)
        source_xml = 'file://%s' % local_source_xml
        j.cloud.system.fs.copyFile(source_xml, destination_xml)
        j.system.fs.remove(local_source_xml)
    	send_mail(locations, 'Upload Successfull', 'platform@cloudscalers.com', emailaddress)
    except Exception as e:
    	send_mail('Upload of backup has failed', 'Upload Failed', 'platform@cloudscalers.com', emailaddress)

    







