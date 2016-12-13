from JumpScale import j
import time
import argparse


def delete_logs(since):
    scl = j.clients.osis.getNamespace('system')
    scl.health.deleteSearch({})
    scl.eco.deleteSearch({'epoch': {'$gt': since}})
    scl.job.deleteSearch({'timeCreate': {'$gt': since}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    now = int(time.time() - 600)
    parser.add_argument('-s', '--since', help='Delete since..', type=int, default=now)
    options = parser.parse_args()
    delete_logs(options.since)
