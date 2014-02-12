[actor] @dbtype:mem,osis
	"""
	API Actor api for performing payments with cryptocurrency
	"""    
			
	method:getPaymentInfo
		"""
		Get the current available credit
		"""
		var:accountId int,, id of the account
		var:coin str,, the code of the currency you want to make a payment with (LTC or BTC currently supported)
		result:dict A json dict containing 'address', 'value' and 'coin':coin
