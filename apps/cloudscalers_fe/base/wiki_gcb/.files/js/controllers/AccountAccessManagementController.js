angular.module('cloudscalers.controllers')
    .controller('AccountAccessManagementController', ['$scope', 'CloudSpace', 'Account', function($scope, CloudSpace, Account) {
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

        $scope.loadSpaceAcl = function() {
            return CloudSpace.get($scope.currentSpace.cloudSpaceId).then(function(space) {
                $scope.currentSpace.acl = space.acl;
            });
        };

        $scope.resetUser();
        $scope.loadSpaceAcl();
        $scope.userError = false;

        $scope.addUser = function() {
            return CloudSpace.addUser($scope.currentSpace, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                $scope.loadSpaceAcl().then(function() {
                    $scope.resetUser();
                });
                $scope.userError = false;
            }, function(result) {
                $scope.userError = true;
            });
        };

        $scope.deleteUser = function(space, user) {
            // TODO: ==================================
            $scope.cloudSpaceUsers.splice($scope.cloudSpaceUsers.indexOf(user), 1);
            $scope.unauthorizedUsers.push(user);
            CloudSpace.deleteUser($scope.currentSpace, user);
        };
    }]);
