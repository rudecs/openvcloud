[actor] @dbtype:mem,osis
	"""
	API Actor api for performing payments with cryptocurrency
	"""    
			
	method:getPaymentInfo
		"""
		Get the info required for making a payment
		"""
		var:accountId int,, id of the account
		var:coin str,, the code of the currency you want to make a payment with (LTC or BTC currently supported)
		result:dict A json dict containing 'address', 'value' and 'coin':coin

    method:getAddressForAccount
    	"""
    	Gets the address assigned to an account, if there is none registered, assign it to the account passed before returning it.
    	"""
    	var:accountId int,, account
    	var:currency str,, code of the cryptocurrency (LTC or BTC)
    	result:dict,, A json dict containing the address, currency and account
	
		