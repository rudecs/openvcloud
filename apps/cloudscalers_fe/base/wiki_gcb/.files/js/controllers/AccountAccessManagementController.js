angular.module('cloudscalers.controllers')
    .controller('AccountAccessManagementController', ['$scope', 'Account', function($scope, Account) {
        $scope.resetUser = function() {
            // For now, we will grant the new user all permissions. See http://<server>/specifications/Security
            $scope.newUser = {
                nameOrEmail: '', 
                access: {
                    R: true,
                    X: true,
                    C: true,
                    D: true,
                    U: true,
                    A: true
                }
            };
        };

        $scope.loadAcl = function() {
            // When this controller is loaded, the currentAccount is not set yet, but currentSpace is.
            return Account.get($scope.currentSpace.accountId).then(function(account) {
                $scope.currentAccount.acl = account.acl;
            });
        };

        $scope.resetUser();
        $scope.loadAcl();
        $scope.userError = false;

        $scope.addUser = function() {
            return Account.addUser($scope.currentAccount, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                $scope.loadAcl().then(function() {
                    $scope.resetUser();
                });
                $scope.userError = false;
            }, function(result) {
                if (result.status == 404)
                    $scope.userError = 'User not found';
                else if (result.status == 500)
                    $scope.userError = 'Internal server error';
                else
                    $scope.userError = 'An error has occurred';
            });
        };

        $scope.deleteUser = function(space, user) {
            Account.deleteUser($scope.currentAccount, user.userGroupId).then(function() {
                $scope.loadAcl();
            });
        };
    }]);
