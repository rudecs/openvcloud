[actor] @dbtype:mem,osis
    """
    Actor for generating negative billing transactions based on cloudusage 
    """
    method:createTransactionStaments
	    """
	    Generates the missing transactions for an account 
	    """
	    var:accountId int,, id of the account
	    
	method:updateBalance
		"""
		Updates the balance for an account given the credit/debit transactions
		"""
		var:accountId int,, id of the account
    
    