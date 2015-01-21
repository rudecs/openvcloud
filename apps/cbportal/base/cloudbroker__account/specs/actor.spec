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

    method:addUser
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        """"
        var:accountname str,, name of the account to add to
        var:username str,,name of the user to be given rights
        var:accesstype str,, R or W

    method:deleteUser
        """
        Delete user from account.
        """"
        var:accountname str,, name of the account to remove from
        var:username str,,name of the user to be removed

    method:rename
        """
        rename account.
        """"
        var:accountname str,, name of the account
        var:name str,,new name

    method:create
        """
        Create Account.
        """"
        var:username str,, name of the account
        var:name str,, Display name
        var:emailaddress str,,email
        var:password str,,password
        var:location str,,locationcode
