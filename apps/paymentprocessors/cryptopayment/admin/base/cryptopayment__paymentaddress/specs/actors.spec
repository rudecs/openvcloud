[actor] @dbtype:mem,osis
	"""
	API Actor api for processing paymentaddresses
	"""
	
    method:create
        """
        Registers an address to be available for customers to make payments on.
        This needs to be a valid address for the given currency.
        """
        var:address str,, address
        var:currency str,, code of the cryptocurrency (LTC or BTC)
        