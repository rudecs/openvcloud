from JumpScale import j
import time, ujson
from datetime import datetime
import calendar

class billingengine_billingengine(j.code.classGetBase()):
    """
    Actor for generating negative billing transactions based on cloudusage

    """
    def __init__(self):

        self._te={}
        self.actorname="billingengine"
        self.appname="billingengine"
        #billingengine_billingengine_osis.__init__(self)

        osiscl = j.core.osis.getClient(user='root')

        class Class():
            pass

        self.billingenginemodels = Class()
        for ns in osiscl.listNamespaceCategories('billing'):
            self.billingenginemodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'billing', ns))
            self.billingenginemodels.__dict__[ns].find = self.billingenginemodels.__dict__[ns].search

        self.cloudbrokermodels = Class()
        for ns in osiscl.listNamespaceCategories('cloudbroker'):
            self.cloudbrokermodels.__dict__[ns] = (j.core.osis.getClientForCategory(osiscl, 'cloudbroker', ns))
            self.cloudbrokermodels.__dict__[ns].find = self.cloudbrokermodels.__dict__[ns].search

    def _get_price_per_hour(self):
        return 1.0

    def _get_last_billing_statement(self, accountId):
        query = {'fields': ['fromTime', 'accountId','id']}
        query['query'] = {'term': {"accountId": accountId}}
        query['size'] = 1
        query['sort'] = [{ "fromTime" : {'order':'desc', 'ignore_unmapped' : True}}]
        results = self.billingenginemodels.billingstatement.find(ujson.dumps(query))['result']
        if len(results) > 0:
            return self.billingenginemodels.billingstatement.get(results[0]['fields']['id'])
        else:
            return None

    def _update_machine_billingstatement(self, machinebillingstatement, machine):
        machinebillingstatement.deletionTime = machine['deletionTime']

        if not machinebillingstatement.deletionTime is 0:
            billmachineuntil = machinebillingstatement.deletionTime
        else:
            billmachineuntil = billing_statement.untilTime

        billmachinefrom = max(billing_statement.fromTime, machinebillingstatement.creationTime)
        number_of_billable_hours = (billmachineuntil - billmachinefrom) / 3600.0
        if (number_of_billable_hours < 1.0): #minimum one hour
            if not machinebillingstatement.deletionTime is 0:
                number_of_billable_hours = 1.0
                #Don't charge double if the machine was partially billed in the previous period
                if (machinebillingstatement.creationTime < billing_statement.fromTime):
                    number_of_billable_hours -= (billing_statement.fromTime * 3600.0)

        price_per_hour = self._get_price_per_hour()
        machinebillingstatement.cost = number_of_billable_hours * price_per_hour

    def _update_usage(self, billing_statement):

        query = {'fields': ['id', 'name', 'accountId']}
        query['query'] = {'term': {'accountId': billing_statement.accountId}}
        results = self.cloudbrokermodels.cloudspace.find(ujson.dumps(query))['result']
        cloudspaces = [res['fields'] for res in results]

        billing_statement.totalCost = 0.0

        for cloudspace in cloudspaces:
            query = {'fields':['id','creationTime','deletionTime','name','cloudspaceId','imageId','sizeId']}

            query['query'] = {'filtered':{
                          "query" : {"term" : { "cloudspaceId" : cloudspace['id'] }},
                          "filter" : { "not":{"range" : {"deletionTime" : {"lt" : billing_statement.fromTime, "gt":0}}}
                                      }
                                 }
                              }

            queryresult = self.cloudbrokermodels.vmachine.find(ujson.dumps(query))['result']
            machines = [res['fields'] for res in queryresult]
            
            if len(machines) is 0:
                continue
            
            cloudspacebillingstatement = next((space for space in billing_statement.cloudspaces if space.cloudspaceId == cloudspace['id']), None)

            if cloudspacebillingstatement is None:
                cloudspacebillingstatement = billing_statement.new_cloudspace()
                cloudspacebillingstatement.name = cloudspace['name']
                cloudspacebillingstatement.cloudspaceId = cloudspace['id']
            
            for machine in machines:
                
                machinebillingstatement = next((machinebs for machinebs in cloudspacebillingstatement.machines if machinebs.machineId==machine['id']),None)
                if machinebillingstatement is None:
                    machinebillingstatement = cloudspacebillingstatement.new_machine()
                    machinebillingstatement.machineId = machine['id']
                    machinebillingstatement.name = machine['name']
                    machinebillingstatement.creationTime = machine['creationTime']
                
                self._update_machine_billingstatement(machinebillingstatement, machine)
                

            cloudspacebillingstatement.totalCost = 0.0
            for machinebillingstatement in cloudspacebillingstatement.machines:
                cloudspacebillingstatement.totalCost += machinebillingstatement.cost

        for cloudspacebillingstatement in billing_statement.cloudspaces:
            billing_statement.totalCost += cloudspacebillingstatement.totalCost


    def _get_credit_transaction(self, currency, reference):
        query = {'fields': ['id', 'currency','reference']}
        query['query'] = {'bool':{'must':[{'term': {"currency": currency.lower()}},{'term':{ 'reference':reference}}]}}
        transactions = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        return None if len(transactions) == 0 else self.cloudbrokermodels.credittransaction.get(transactions[0]['fields']['id'])

    def _save_billing_statement(self,billing_statement):
        self.billingenginemodels.billingstatement.set(billing_statement)
        creditTransaction = self._get_credit_transaction('USD', billing_statement.id)
        if creditTransaction is None:
            creditTransaction = self.cloudbrokermodels.credittransaction.new()
            creditTransaction.currency = 'USD'
            creditTransaction.accountId = billing_statement.accountId
            creditTransaction.reference = str(billing_statement.id)
            creditTransaction.status = 'DEBIT'
            creditTransaction.time = billing_statement.untilTime - (3600 * 24)

        creditTransaction.amount = -billing_statement.totalCost
        creditTransaction.credit = -billing_statement.totalCost
        self.cloudbrokermodels.credittransaction.set(creditTransaction)

    def _find_earliest_billable_action_time(self, accountId):
        query = {'fields': ['id', 'name', 'accountId']}
        query['query'] = {'term': {"accountId": accountId}}
        results = self.cloudbrokermodels.cloudspace.find(ujson.dumps(query))['result']
        cloudspaces = [res['fields'] for res in results]
        cloudspaceterms = []
        for cloudspace in cloudspaces:
            cloudspaceterms.append({'term':{'cloudspaceId':cloudspace['id']}})
        query = {'fields':['id','creationTime']}
        query['query'] = {'bool':{'should':cloudspaceterms}}
        query['size'] = 1
        query['sort'] = [{ "creationTime" : {'order':'asc', 'ignore_unmapped' : True}}]

        results = self.cloudbrokermodels.vmachine.find(ujson.dumps(query))['result']
        return results[0]['fields']['creationTime'] if len(results) > 0 else None


    def _create_empty_billing_statements(self, fromTime, untilTime, accountId):
        untilMonthDate = datetime.utcfromtimestamp(untilTime).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        untilMonthTime = calendar.timegm(untilMonthDate.timetuple())
        fromMonthDate = datetime.utcfromtimestamp(fromTime).replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        fromMonthTime = calendar.timegm(fromMonthDate.timetuple())
        billingstatements = []
        while (fromMonthTime <= untilMonthTime):
            nextMonthTime = self._addMonth(fromMonthTime)
            billingstatement = self.billingenginemodels.billingstatement.new()
            billingstatement.fromTime = fromMonthTime
            billingstatement.untilTime = nextMonthTime
            billingstatement.accountId = accountId
            billingstatement.cloudspaces = []
            billingstatements.append(billingstatement)
            fromMonthTime = nextMonthTime

        return billingstatements

    def _addMonth(self, timestamp):
        timestampdatetime = datetime.utcfromtimestamp(timestamp)
        monthbeginning = timestampdatetime.replace(day=1,minute=0,second=0,microsecond=0)
        if monthbeginning.month == 12:
            nextmonthbeginning = monthbeginning.replace(year=monthbeginning.year + 1, month=1)
        else:
            nextmonthbeginning = monthbeginning.replace(month=monthbeginning.month+1)

        return calendar.timegm(nextmonthbeginning.timetuple())

    def createTransactionStaments(self, accountId, **kwargs):
        """
        Generates the missing billing statements and debit transactions for an account
        param:accountId id of the account
        """
        now = int(time.time())
        last_billing_statement = self._get_last_billing_statement(accountId)
        next_billing_statement_time = None
        if not last_billing_statement is None:
            self._update_usage(last_billing_statement)
            self._save_billing_statement(last_billing_statement)
            next_billing_statement_time = self._addMonth(last_billing_statement.fromTime)
        else:
            next_billing_statement_time = self._find_earliest_billable_action_time(accountId)

        if next_billing_statement_time is None:
            next_billing_statement_time = now

        for billing_statement in self._create_empty_billing_statements(next_billing_statement_time, now, accountId):
            self._update_usage(billing_statement)
            self._save_billing_statement(billing_statement)

        self.updateBalance(accountId)


    def updateBalance(self, accountId, **kwargs):
        """
        Updates the balance for an account given the credit/debit transactions
        param:accountId id of the account
        """
        #For now, sum here, as of ES 1.0, can be done there
        query = {'fields': ['time', 'credit', 'status']}
        query['query'] = {'bool':{'must':[{'term': {"accountId": accountId}}],'must_not':[{'term':{'status':'UNCONFIRMED'.lower()}}]}}
        results = self.cloudbrokermodels.credittransaction.find(ujson.dumps(query))['result']
        history = [res['fields'] for res in results]
        balance = 0.0
        for transaction in history:
            balance += float(transaction['credit'])
            #TODO: put in processed (but only save after updating the balance)

        newbalance = self.cloudbrokermodels.creditbalance.new()
        newbalance.accountId = accountId
        newbalance.time = int(time.time())
        newbalance.credit = balance
        self.cloudbrokermodels.creditbalance.set(newbalance)
        #TODO: remove older credit balances
