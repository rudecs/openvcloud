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
    
    
    def getCreditBalance(self, accountId):
        """
        Get the current available credit

        param:accountId id of the account
        """
        query = {'fields': ['time', 'credit', 'status']}
        query['query'] = {'bool':{'must':[{'term': {"accountId": accountId}}],'must_not':[{'term':{'status':'UNCONFIRMED'.lower()}}]}}
        results = self.cloudbrokermodels.credittransaction.search(ujson.dumps(query))['result']
        history = [res['fields'] for res in results]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
        return balance