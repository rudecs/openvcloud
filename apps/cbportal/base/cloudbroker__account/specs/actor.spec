[actor] @dbtype:mem,fs
    """
    Operator actions for interventions on accounts
    """
    method:disable
        """
        disable an account.
        """
        var:accountId int,,ID of account
        var:reason str,,reason of disabling the account

    method:enable
        """
        enable an account.
        """
        var:accountId int,,ID of account to enable
        var:reason str,,reason of enabling the account

    method:delete
        """
        Complete delete an account from the system
        """"
        var:accountId int,,ID of account to delete
        var:reason str,,reason for deleting the account

    method:addUser
        """
        Give a user access rights.
        Access rights can be 'R' or 'W'
        """"
        var:accountId int,,ID of account to add to
        var:username str,,name of the user to be given rights
        var:accesstype str,, R or W

    method:deleteUser
        """
        Delete user from account.
        """"
        var:accountId int,,ID of account to remove from
        var:username str,,name of the user to be removed
        var:recursivedelete bool,, recursively delete access rights from owned cloudspaces and vmachines

    method:rename
        """
        rename account.
        """"
        var:accountId int,,ID of account
        var:name str,,new name

    method:create
        """
        Create Account.
        """"
        var:name str,, Display name
        var:username str,, name of the account
        var:emailaddress str,,email
        var:location str,,locationcode
