from JumpScale import j
import time, ujson
from datetime import datetime
import calendar
from billingenginelib import pricing

class billingengine_billingengine(j.code.classGetBase()):
    """
    Actor for generating negative billing transactions based on cloudusage

    """
    def __init__(self):

        self._te={}
        self.actorname="billingengine"
        self.appname="billingengine"

        self.billingenginemodels = j.clients.osis.getNamespace('billing')
        self.cloudbrokermodels = j.clients.osis.getNamespace('cloudbroker')

        self._pricing = pricing.pricing()

    def _get_last_billing_statement(self, accountId):
        query = {'$query': {'accountId': accountId},
                 '$orderby': [('fromTime', -1)]}
        results = self.billingenginemodels.billingstatement.search(query, size=1)[1:]
        if len(results) > 0:
            return self.billingenginemodels.billingstatement.get(results[0]['id'])
        else:
            return None

    def _get_number_of_billable_hours(self, creationTime, deletionTime, fromTime, untilTime):
        if not deletionTime == 0:
            billuntil = deletionTime
        else:
            billuntil = untilTime

        billfrom = max(fromTime, creationTime)
        number_of_billable_hours = (billuntil - billfrom) / 3600.0
        if (number_of_billable_hours < 1.0): #minimum one hour
            if not deletionTime == 0: #but only if it is destroyed
                #Don't charge double if the machine was partially billed in the previous period
                number_of_hours_in_previous_calculations = max(0.0,(fromTime - creationTime) / 3600.0)
                if (number_of_hours_in_previous_calculations < 1.0):
                    number_of_billable_hours = 1.0 - number_of_hours_in_previous_calculations

        return number_of_billable_hours

    def _update_machine_billingstatement(self, machinebillingstatement, machine, fromTime, untilTime):
        machinebillingstatement.deletionTime = machine['deletionTime']

        number_of_billable_hours = self._get_number_of_billable_hours(
                                                                     machinebillingstatement.creationTime, 
                                                                     machinebillingstatement.deletionTime, 
                                                                     fromTime, 
                                                                     untilTime)

        price_per_hour = self._pricing.get_machine_price_per_hour(machine)
        machinebillingstatement.cost = number_of_billable_hours * price_per_hour

    def _update_usage(self, billing_statement):

        query = {'accountId': billing_statement.accountId, 
                 '$or': [{'deletionTime': 0}, {'deletionTime': {'$gt': billing_statement.fromTime}}], 
                 'creationTime': {'$lt': billing_statement.untilTime}}
        cloudspaces = self.cloudbrokermodels.cloudspace.search(query)[1:]


        for cloudspace in cloudspaces:
            query = {'cloudspaceId': cloudspace['id'], 
                     '$or': [{'deletionTime': 0}, {'deletionTime': {'$gt': billing_statement.fromTime}}], 
                     'creationTime': {'$lt': billing_statement.untilTime}}
            machines = self.cloudbrokermodels.vmachine.search(query)[1:]

            cloudspacebillingstatement = next((space for space in billing_statement.cloudspaces if space.cloudspaceId == cloudspace['id']), None)

            if cloudspacebillingstatement is None:
                cloudspacebillingstatement = billing_statement.new_cloudspace()
                cloudspacebillingstatement.name = cloudspace['name']
                cloudspacebillingstatement.cloudspaceId = cloudspace['id']
            
            #Charge for the cloudspace 
            number_of_billable_hours = self._get_number_of_billable_hours(
                                                                          cloudspace['creationTime'], 
                                                                          cloudspace['deletionTime'], 
                                                                          billing_statement.fromTime, 
                                                                          billing_statement.untilTime)
            cloudspacebillingstatement.cloudspaceCost = number_of_billable_hours * self._pricing.get_cloudspace_price_per_hour()
            
            #Charge for the machines
            for machine in machines:

                machinebillingstatement = next((machinebs for machinebs in cloudspacebillingstatement.machines if machinebs.machineId==machine['id']),None)
                if machinebillingstatement is None:
                    machinebillingstatement = cloudspacebillingstatement.new_machine()
                    machinebillingstatement.machineId = machine['id']
                    machinebillingstatement.name = machine['name']
                    machinebillingstatement.creationTime = machine['creationTime']

                self._update_machine_billingstatement(machinebillingstatement, machine, billing_statement.fromTime, billing_statement.untilTime)


            cloudspacebillingstatement.totalCost = cloudspacebillingstatement.cloudspaceCost
            for machinebillingstatement in cloudspacebillingstatement.machines:
                cloudspacebillingstatement.totalCost += machinebillingstatement.cost

        #First cloudspace is free and an account always has at least one cloudspace
        #So substract 1 cloudspace for the total billing time
        if (len(cloudspaces) > 0):
            cloudspacesbycreationtime = sorted(cloudspaces, key=lambda x: x['creationTime'])
            creationTime = cloudspacesbycreationtime[0]['creationTime']
            
            cloudspacesbydeletiontime = sorted(cloudspaces, key=lambda x: x['deletionTime'])
            deletionTime = 0
            if (cloudspacesbydeletiontime[0]['deletionTime'] > 0):
                deletionTime = cloudspacesbydeletiontime[-1]['deletionTime']
            
            number_of_billable_hours = self._get_number_of_billable_hours(
                                                                          creationTime, 
                                                                          deletionTime, 
                                                                          billing_statement.fromTime, 
                                                                          billing_statement.untilTime)
            billing_statement.freeCloudspaceCost = -(number_of_billable_hours * self._pricing.get_cloudspace_price_per_hour())
        else:
            billing_statement.freeCloudspaceCost = 0.0

        #Calculate total cost for the account
        billing_statement.totalCost = billing_statement.freeCloudspaceCost
        for cloudspacebillingstatement in billing_statement.cloudspaces:
            billing_statement.totalCost += cloudspacebillingstatement.totalCost


    def _get_credit_transaction(self, currency, reference):
        query = {'currency': currency, 'reference': str(reference)}
        transactions = self.cloudbrokermodels.credittransaction.search(query)[1:]
        return None if len(transactions) == 0 else self.cloudbrokermodels.credittransaction.get(transactions[0]['id'])


    def _addMonth(self, timestamp):
        timestampdatetime = datetime.utcfromtimestamp(timestamp)
        monthbeginning = timestampdatetime.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        if monthbeginning.month == 12:
            nextmonthbeginning = monthbeginning.replace(year=monthbeginning.year + 1, month=1)
        else:
            nextmonthbeginning = monthbeginning.replace(month=monthbeginning.month+1)

        return calendar.timegm(nextmonthbeginning.timetuple())

    def _save_billing_statement(self,billing_statement, now):
        result = self.billingenginemodels.billingstatement.set(billing_statement)
        if billing_statement.id == '':
            billing_statement.id = str(result[0])
        creditTransaction = self._get_credit_transaction('USD', billing_statement.id)
        if creditTransaction is None:
            creditTransaction = self.cloudbrokermodels.credittransaction.new()
            creditTransaction.currency = 'USD'
            creditTransaction.accountId = billing_statement.accountId
            creditTransaction.reference = str(billing_statement.id)
            creditTransaction.status = 'DEBIT'

        creditTransaction.time = self._addMonth(billing_statement.fromTime)
        if creditTransaction.time > now:
            creditTransaction.time = now
        else:
            creditTransaction.time -= (3600 * 24)

        creditTransaction.amount = -billing_statement.totalCost
        creditTransaction.credit = -billing_statement.totalCost
        self.cloudbrokermodels.credittransaction.set(creditTransaction)

    def _find_earliest_billable_action_time(self, accountId):
        query = {'accountId': accountId}
        cloudspaces = self.cloudbrokermodels.cloudspace.search(query)[1:]
        cloudspaceids = [ cloudspace['id'] for cloudspace in cloudspaces ]
        query = {'$query': {'cloudspaceId': {'$in': cloudspaceids}}, 
                 '$orderby': [('creationTime', 1)]
                }
        results = self.cloudbrokermodels.vmachine.search(query, size=1)[1:]
        return results[0]['creationTime'] if len(results) > 0 else None


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

    def createTransactionStaments(self, accountId, **kwargs):
        """
        Generates the missing billing statements and debit transactions for an account
        param:accountId id of the account
        """
        now = int(time.time())
        last_billing_statement = self._get_last_billing_statement(accountId)
        next_billing_statement_time = None
        if not last_billing_statement is None:
            last_billing_statement.untilTime = min(now,self._addMonth(last_billing_statement.fromTime))
            self._update_usage(last_billing_statement)
            self._save_billing_statement(last_billing_statement, now)
            next_billing_statement_time = self._addMonth(last_billing_statement.fromTime)
        else:
            next_billing_statement_time = self._find_earliest_billable_action_time(accountId)

        if next_billing_statement_time is None:
            next_billing_statement_time = now

        for billing_statement in self._create_empty_billing_statements(next_billing_statement_time, now, accountId):
            billing_statement.untilTime = min(now,self._addMonth(billing_statement.fromTime))
            self._update_usage(billing_statement)
            self._save_billing_statement(billing_statement, now)

        self.updateBalance(accountId)


    def updateBalance(self, accountId, **kwargs):
        """
        Updates the balance for an account given the credit/debit transactions
        param:accountId id of the account
        """
        query = {'accountId': accountId, 'status': {'$ne': 'UNCONFIRMED'}}
        history = self.cloudbrokermodels.credittransaction.search(query)[1:]
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
