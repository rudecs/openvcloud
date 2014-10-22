from JumpScale import j
import time
import JumpScale.grid.osis
from JumpScale.portal.portal.auth import auth

class cloudbroker_finance(j.code.classGetBase()):
    """
    gateway to grid
    """
    def __init__(self):
        self._te={}
        self.actorname="finance"
        self.appname="cloudbroker"

        cl = j.core.osis.getClient(user='root')
        self.acclient = j.core.osis.getClientForCategory(cl,'cloudbroker','account')
        self.credittransactionclient = j.core.osis.getClientForCategory(cl,'cloudbroker','credittransaction')

    @auth(['finance',])
    def changeCredit(self, accountname, amount, message, **kwargs):
        accounts = self.acclient.simpleSearch({'name': accountname})
        if not accounts:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("404", headers)
            return 'Account name not found'
        account_id = accounts[0]['id']

        if len(message) > 30:
            ctx = kwargs["ctx"]
            headers = [('Content-Type', 'application/json'), ]
            ctx.start_response("400", headers)
            return 'Message is too long'

        credittransaction = self.credittransactionclient.new()
        credittransaction.accountId = account_id
        credittransaction.amount = float(amount)
        credittransaction.credit = float(amount)
        credittransaction.currency = 'USD'
        credittransaction.comment = message
        credittransaction.status = 'CREDIT' if amount >= 0 else 'DEBIT'
        credittransaction.time = int(time.time())

        self.credittransactionclient.set(credittransaction)
        return True