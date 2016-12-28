descr = """
Write readme file on http
"""

category = "cloudbroker"
organization = "greenitglobe"
author = "deboeckj@greenitglobe.com"
license = "bsd"
version = "1.0"
roles = ['storagedriver']
async = True
timeout = 60 * 60


def action(link, username, passwd, path):
    import os
    import requests
    basepath = os.path.join(link, path.strip('/'))

    readme = '''
This folder contains an exported Virtual machine.

The format of the export is OVF, see https://www.dmtf.org/sites/default/files/standards/documents/DSP0243_2.0.0.pdf
Rather then having one big OVA file, the OVA file was compressed with gzip and split into pieces of 100MB.
To reconstruct the OVF file, ready to import into OVF complianed hypervisors issue the following commands.

Linux / macOS:
cat export.ova.gz.* > export.ova.gz
gunzip export.ova.gz

Windows:
copy /b export.ova.gz.* export.ova.gz
Extract export.ova.gz with one of the following tools 7zip gunzip winrar
    '''

    res = requests.put(os.path.join(basepath, 'README.txt'), data=readme, auth=(username, passwd))
    if res.status_code > 300:
        raise RuntimeError("Failed to upload README file: {}:{}".format(res.status_code, res.text))
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', default='admin')
    parser.add_argument('-p', '--password', default='admin')
    parser.add_argument('-url', '--url')
    parser.add_argument('-path', '--path')
    options = parser.parse_args()
    action(options.url, options.user, options.password, options.path, "xml", [options.disk])
