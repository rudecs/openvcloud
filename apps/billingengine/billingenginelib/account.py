from JumpScale import j
from JumpScale import portal
import ujson

class account(object):
    def __init__(self):

        self.cloudbrokermodels = j.core.osis.getClientForNamespace('cloudbroker')

    def isPayingCustomer(self, accountId):
        query = {'accountId': accountId, 'status': {'$ne': 'PROCESSED'}}
        payments = self.cloudbrokermodels.credittransaction.search(query)[0]
        return payments > 0


    def getCreditBalance(self, accountId):
        """
        Get the current available credit

        param:accountId id of the account
        """
        query = {'accountId': accountId, 'status': {'$ne': 'UNCONFIRMED'}}
        history = self.cloudbrokermodels.credittransaction.search(query)[1:]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
        return balance
