[actor] @dbtype:mem,osis
    """
    API Actor api for managing account
    """
    method:create
        """
        Create a extra an account (Method not implemented)
        """
        var:name str,,name of account to create
        var:access list,,list of ids of users which have full access to this account
        result:int, returns id of account created

    method:delete
        """
        Delete an account (Method not implemented)
        """
        var:accountId int,, id of the account
        result:bool, True if deletion was successful

    method:list
        """
        List all accounts the user has access to
        """
        result:[], list with every element containing details of a account as a dict

    method:update
        """
        Update an account name (Method not implemented)
        """
        var:accountId int,, id of the account to change
        var:name str,, name of the account
        result:int, id of account updated

    method:addUser
        """
        Give a registered user access rights
        """
        var:accountId int,, id of the account
        var:userId str,, username or emailaddress of the user to grant access
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully

    method:updateUser
        """
        Update user access rights
        """
        var:accountId int,, id of the account
        var:userId str,, userid/email for registered users or emailaddress for unregistered users
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user access was updated successfully

    method:deleteUser
        """
        Revoke user access from the account
        """
        var:accountId int,, id of the account
        var:userId str,, id or emailaddress of the user to remove
        var:recursivedelete bool,False, recursively revoke access rights from owned cloudspaces and vmachines @optional
        result: bool, True if user access was revoked from account

    method:get
        """
        Get account details
        """
        var:accountId int,, id of the account
        result:dict, dict with the account details


    method:listTemplates
        """
        List templates which can be managed by this account
        """
        var:accountId int,, id of the account
        result:dict, dict with the template images for the given account

    method:getCreditBalance
        """
        Get the current available credit balance
        """
        var:accountId int,, id of the account
        result:dict json dict containing the available credit

    method:getCreditHistory
        """
        Get all the credit transactions (positive and negative) for this account
        """
        var:accountId int,, id of the account
        result:[], list with the transactions details each as a dict

    method:addExternalUser
        """
        Give an unregistered user access rights by sending an invite email
        """
        var:accountId int,, id of the account
        var:emailaddress str,, emailaddress of the unregistered user that will be invited
        var:accesstype str,, 'R' for read only access, 'RCX' for Write and 'ARCXDU' for Admin
        result:bool, True if user was added successfully

    method:getConsumedCloudUnits
        """
        Calculate the currently consumed cloud units for all cloudspaces in the account.

        Calculated cloud units are returned in a dict which includes:
        - CU_M: consumed memory in GB
        - CU_C: number of cpu cores
        - CU_D: consumed vdisk storage in GB
        - CU_I: number of public IPs
        """
        var:accountId int,, id of the account consumption should be calculated for
        result:dict, dict with the consumed cloud units

    method:getConsumedCloudUnitsByType
        """
        Calculate the currently consumed cloud units of the specified type for all cloudspaces
        in the account.

        Possible types of cloud units are include:
        - CU_M: returns consumed memory in GB
        - CU_C: returns number of virtual cpu cores
        - CU_D: returns consumed virtual disk storage in GB
        - CU_I: returns number of public IPs
        """
        var:accountId int,, id of the account consumption should be calculated for
        var:cutype str,, cloud unit resource type
        result:float, float/int for the consumed cloud unit of the specified type