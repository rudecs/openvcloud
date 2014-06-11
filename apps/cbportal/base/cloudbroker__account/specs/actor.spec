[actor] @dbtype:mem,fs
    """
    account manager
    """    
    method:disable
        """     
        disable an account.
        """
        var:accountname str,,name of account
        var:reason str,,reason of disabling the account

    method:enable
        """     
        enable an account.
        """
        var:accountname str,,name of account
        var:reason str,,reason of enabling the account
