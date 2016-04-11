from JumpScale import j
import time
from JumpScale.portal.portal.auth import auth
from JumpScale.portal.portal import exceptions
from cloudbrokerlib.baseactor import BaseActor

class cloudbroker_finance(BaseActor):
    """
    gateway to grid
    """
    @auth(['finance',])
    def changeCredit(self, accountId, amount, message, **kwargs):
        if not self.models.account.exists(accountId):
            raise exceptions.NotFound('Account not found')
        if len(message) > 30:
            raise exceptions.BadRequest('Message is too long')

        credittransaction = self.models.credittransaction.new()
        credittransaction.accountId = accountId
        credittransaction.amount = float(amount)
        credittransaction.credit = float(amount)
        credittransaction.currency = 'USD'
        credittransaction.comment = message
        credittransaction.status = 'CREDIT' if float(amount) >= 0 else 'DEBIT'
        credittransaction.time = int(time.time())

        self.models.credittransaction.set(credittransaction)
        return True
