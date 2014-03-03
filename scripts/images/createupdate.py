#!/usr/bin/env python
from JumpScale import j
from JumpScale.baselib.cmdutils import ArgumentParser
from jinja2 import Template
import os

DOMAIN = 'cloudscalers'

def getJPackage(name, description):
    jps = j.packages.find(DOMAIN, name)
    if jps:
        print 'Found JPackage %s will update' % name
        return jps[0]
    print 'Could not find JPackage with name %s will create new' % name
    return j.packages.create(DOMAIN, name, version='1.0', description=description, supportedPlatforms=['generic'])

def downloadImage(jp, url):
    destination = j.system.fs.joinPaths(jp.getPathFilesPlatform('generic'), 'root', 'mnt', 'vmstor', 'templates')
    j.system.fs.createDir(destination)
    destinationfile = j.system.fs.joinPaths(destination, '%s.qcow2' % jp.name)
    j.system.net.download(url, destinationfile)
    return destinationfile

def cleanup(jp):
    j.system.fs.removeDirTree(jp.getPathFiles())
    j.system.fs.createDir(jp.getPathFilesPlatform('generic'))


def writeConfigure(jp, name, description, imagepath, type_):
    dirpath = j.system.fs.getDirName(os.path.abspath(__file__))
    tmppath = j.system.fs.joinPaths(dirpath, 'configure.tmpl')
    template = Template(j.system.fs.fileGetContents(tmppath))
    image = j.system.fs.getBaseName(imagepath)
    result = template.render(type=type_, size=args.size, name=name, description=description, imagepath=image)
    configurepath = j.system.fs.joinPaths(jp.getPathMetadata(), 'actions', 'install.configure.py')
    j.system.fs.writeFile(configurepath, result)


def main(args):
    print 'Updating Metadata'
    j.packages.updateMetaDataAll()
    jp = getJPackage(args.name, args.description)
    print 'Cleanup old stuff'
    cleanup(jp)
    print 'Downloading Image'
    imagepath = downloadImage(jp, args.url)
    print 'Writing configure tasklet'
    writeConfigure(jp, args.name, args.description, imagepath, args.type)
    print 'Uploading Image'
    jp.upload()
    print 'Publishing'
    j.packages.publishDomain(DOMAIN, 'Automated image updater')


if __name__ == '__main__':
    j.application.start('packager')
    parser = ArgumentParser()
    parser.add_argument('-n', '--name')
    parser.add_argument('-d', '--description')
    parser.add_argument('-u', '--url')
    parser.add_argument('-t', '--type')
    parser.add_argument('-s', '--size', help='Size in GB')
    args = parser.parse_args()
    main(args)
    j.application.stop()
