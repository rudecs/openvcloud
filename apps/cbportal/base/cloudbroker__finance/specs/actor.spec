[actor] @dbtype:mem,fs
    """
    finance manager
    """    
    method:changeCredit
        """     
        add or remove credit to an account with certain amount.
        """
        var:accountname str,,name of account
        var:amount str,,amount to be transferred (positive is credit, negative is debit)
        var:message str,,message. Must be less than 30 characters