[actor] @dbtype:mem,osis
	"""
	API Actor api for processing payments with cryptocurrency
	"""    
    
    
    method:process
    	"""
    	Process the transactions for a given currency (should become jumpscript)
    	"""
    	var:currency str,, code of the currency to process transactions from (LTC and BTC currently supported)