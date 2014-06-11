[actor] @dbtype:mem,fs
    """
    finance manager
    """    
    method:addCredit
        """     
        add credit to an account with certain amount.
        """
        var:accountname str,,name of account
        var:amount str,,amount to be transferred
        var:message str,,message. Must be less than 30 characters