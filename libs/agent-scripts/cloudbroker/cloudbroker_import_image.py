from JumpScale import j

descr = """
Import image
"""

category = "cloudbroker"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
queue = 'io'
async = True
timeout = 60 * 60 * 24


def action(url, volumeid, eventstreamid, disksize, ovs_connection, istemplate=False):
    from CloudscalerLibcloud import openvstorage
    import time
    import math
    pcl = j.clients.portal.getByInstance('main')
    basename = j.system.fs.getBaseName(url)
    title =  'Downloading Image {}'.format(basename)
    message = 'Download @ {:.2f}%'
    level = 'info'
    data = {'lastreporttime': 0}
    destinationpath, diskguid = volumeid.split('@')
    destination = destinationpath.replace('://', ':')

    def resize_disk(newsize):
        diskextend = j.clients.redisworker.getJumpscriptFromName('greenitglobe', 'extend_disk')
        diskextend.write()
        diskextend.load()
        diskextend.executeInProcess(ovs_connection, newsize, diskguid)

    def reporthook(percent):
        now = time.time()
        if now - data['lastreporttime'] < 5:
            return
        data['lastreporttime'] = now
        pcl.actors.system.contentmanager.sendEvent(title, message.format(percent), level, eventstreamid)

    def downloadhook(chunknr, chunksize, totalsize):
        percent = ((chunknr * float(chunksize)) / totalsize) * 100
        reporthook(percent)


    tmpdir = j.system.fs.joinPaths(j.dirs.varDir, 'tmp')
    j.system.fs.createDir(tmpdir)
    tmpfile = j.system.fs.getTempFileName(tmpdir)
    try:
        j.system.net.download(url, tmpfile, reporthook=downloadhook)
        pcl.actors.system.contentmanager.sendEvent(title, message.format(100), level, eventstreamid)
        title = 'Converting Image {}'.format(basename)
        message = 'Convert @ {:.2f}%'
        data['lastreporttime'] = 0
        imginfo = j.system.platform.qemu_img.info(tmpfile, unit='G')
        imgformat = imginfo['file format']
        imgsize = int(math.ceil(imginfo['virtual size']))
        print 'img size {} disk size {}'.format(imgsize, disksize)
        if imgsize > disksize:
            resize_disk(imgsize)
        j.system.platform.qemu_img.convert(tmpfile, imgformat, destination, 'raw', logger=reporthook, createTarget=False)

    finally:
        j.system.fs.remove(tmpfile)
    if istemplate:
        openvstorage.setAsTemplate(destination)

    return imgsize

