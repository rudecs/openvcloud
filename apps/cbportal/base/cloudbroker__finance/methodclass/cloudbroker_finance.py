from JumpScale import j
import time
from JumpScale.portal.portal.auth import auth
from cloudbrokerlib.baseactor import BaseActor

class cloudbroker_finance(BaseActor):
    """
    gateway to grid
    """
    @auth(['finance',])
    def changeCredit(self, accountname, amount, message, **kwargs):
        accounts = self.models.account.search({'name': accountname})[1:]
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

        credittransaction = self.models.credittransaction.new()
        credittransaction.accountId = account_id
        credittransaction.amount = float(amount)
        credittransaction.credit = float(amount)
        credittransaction.currency = 'USD'
        credittransaction.comment = message
        credittransaction.status = 'CREDIT' if float(amount) >= 0 else 'DEBIT'
        credittransaction.time = int(time.time())

        self.models.credittransaction.set(credittransaction)
        return True
