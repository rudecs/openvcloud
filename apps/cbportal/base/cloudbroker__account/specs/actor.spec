[actor] @dbtype:mem,fs
    """
    Operator actions for interventions on accounts
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
        var:accountname str,,name of the account to enable
        var:reason str,,reason of enabling the account

    method:delete
        """
        Complete delete an account from the system
        """"
        var:accountname str,, name of the account to delete
        var:reason str,,reason for deleting the account
