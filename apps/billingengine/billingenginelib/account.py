from JumpScale import j
from JumpScale import portal
import ujson

class account(object):
    def __init__(self):

        self.cloudbrokermodels = j.core.osis.getClientForNamespace('cloudbroker')

    def isPayingCustomer(self, accountId):
        query = {'fields':['accountId']}

        query['query'] = {
                          'filtered':{
                                      "query" :{
                                                "bool":{"must":[
                                                                {"term":{"status":"credit"}},
                                                                {"term" : { "accountId" : accountId }}
                                                                ]
                                                        }
                                                },
                                      "filter" : {"exists":{"field":"reference"}}
                                      }
                          }

        queryresult = self.cloudbrokermodels.credittransaction.search(ujson.dumps(query))['result']
        payments = [res['fields'] for res in queryresult]
        return len(payments) > 0