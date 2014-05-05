#!/usr/bin/env python
from argparse import ArgumentParser
import sys

from JumpScale import j
from JumpScale import portal




def main(args):
    cl = j.core.osis.getClient(user='root')
    acclient = j.core.osis.getClientForCategory(cl,'cloudbroker','account')
    accounts = acclient.simpleSearch({'name': args.accountname})
    if len(accounts) is 0:
        print "Accountname not found"
        return 1
    account_id = accounts[0]['id']

    credittransactionclient = j.core.osis.getClientForCategory(cl,'cloudbroker','credittransaction')
    credittransaction = credittransactionclient.new()
    credittransaction.accountId = account_id
    credittransaction.amount = float(args.usd)
    credittransaction.credit = float(args.usd)
    credittransaction.currency = 'USD'
    credittransaction.comment = args.comment
    credittransaction.status = 'CREDIT'
    
    credittransactionclient.set(credittransaction)
    return 0

if __name__ == '__main__':
    
    try:
        
        parser = ArgumentParser()
        parser.add_argument('-a', '--accountname')
        parser.add_argument('-u','--usd')
        parser.add_argument('-c', '--comment')
        args = parser.parse_args()
        sys.exit(main(args))
        

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        sys.exit(0)
    
