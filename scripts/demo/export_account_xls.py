from JumpScale import j
import argparse
import os
import xlwt
import pprint
import capnp
import CloudscalerLibcloud
from datetime import datetime
from os import listdir


def main(options):
    now = datetime.utcnow()
    hour = now.hour
    day = now.day
    month = now.month
    year = now.year

    capnp.remove_import_hook()
    schemapath = os.path.join(os.path.dirname(CloudscalerLibcloud.__file__), 'schemas', 'resourcemonitoring.capnp')
    resources_capnp = capnp.load(schemapath)
    root_path = "/opt/jumpscale7/var/resourcetracking"
    accounts = listdir(root_path)

    book = xlwt.Workbook(encoding='utf-8')
    nosheets = True
    for account in accounts:
        file_path = os.path.join(root_path, str(account), str(year), str(month), str(day), str(hour), 'account_capnp.bin')
        while not os.path.exists(file_path) and hour != 0:
            hour -= 1
            file_path = os.path.join(root_path, str(account), str(year), str(month), str(day), str(hour), 'account_capnp.bin')
        if not os.path.exists(file_path):
            continue
        nosheets = False
        sheet = book.add_sheet("account %s" % account)
        sheet.write(0, 0, 'Cloud Space ID')
        sheet.write(0, 1, 'Machine Count')
        sheet.write(0, 2, 'Total Memory')
        sheet.write(0, 3, 'Total VCPUs')
        sheet.write(0, 4, 'Disk Size')
        sheet.write(0, 5, 'Disk IOPS Read')
        sheet.write(0, 6, 'Disk IOPS Write')
        sheet.write(0, 7, 'NICs TX')
        sheet.write(0, 8, 'NICs RX')
        try:
            with open(file_path, 'rb') as f:
                account_obj = resources_capnp.Account.read(f)
                if options.debug:
                    pprint.pprint(account_obj.to_dict())
                for idx, cs in enumerate(account_obj.cloudspaces):
                    cs_id = cs.cloudSpaceId
                    machines = len(cs.machines)
                    vcpus = 0
                    mem = 0
                    disksize = 0
                    disk_iops_read = 0
                    disk_iops_write = 0
                    nics_tx = 0
                    nics_rx = 0
                    for machine in cs.machines:
                        vcpus += machine.vcpus
                        mem += machine.mem
                        for disk in machine.disks:
                            disk_iops_read += disk.iopsRead
                            disk_iops_write += disk.iopsWrite
                            disksize += disk.size
                        for nic in machine.networks:
                            nics_tx += nic.tx
                            nics_rx += nic.rx
                    sheet.write(idx + 1, 0, cs_id)
                    sheet.write(idx + 1, 1, machines)
                    sheet.write(idx + 1, 2, mem)
                    sheet.write(idx + 1, 3, vcpus)
                    sheet.write(idx + 1, 4, disksize)
                    sheet.write(idx + 1, 5, disk_iops_read)
                    sheet.write(idx + 1, 6, disk_iops_write)
                    sheet.write(idx + 1, 7, nics_tx)
                    sheet.write(idx + 1, 8, nics_rx)
        except Exception as e:
            print(e)

    if nosheets is False:
        book.save('example.xls')
    else:
        print('No data found')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    options = parser.parse_args()
    main(options)
