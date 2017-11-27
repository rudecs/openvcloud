#!/usr/bin/env python
from argparse import ArgumentParser
import json
import sys, random, string
import boto, boto.s3.connection



def createbuckets(s3server, accesskey, secretkey):
    conn = boto.connect_s3(accesskey,secretkey,is_secure=True,host=s3server,calling_format = boto.s3.connection.OrdinaryCallingFormat(),debug=2)
    buckets = conn.get_all_buckets()
    for x in range(0,3-len(buckets)):
        bucketname = ''.join(random.choice(string.ascii_lowercase) for _ in range(15))
        conn.create_bucket(bucketname)

def main(args):

    with open(args.usersfile) as json_file:
        userdata = json.load(json_file)

    for user in userdata:
        accesskey = user['keys'][0]['access_key']
        secretkey = user['keys'][0]['secret_key']
        createbuckets(args.s3server, accesskey,secretkey)




if __name__ == '__main__':

    try:

        parser = ArgumentParser()
        parser.add_argument('-u', '--usersfile')
        parser.add_argument('-s', '--s3server')
        args = parser.parse_args()
        main(args)

        sys.exit(0)
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        sys.exit(0)

