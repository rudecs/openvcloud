angular.module('cloudscalers.controllers')
    .controller('AccountAccessManagementController', ['$scope', 'CloudSpace', 'Account', function($scope, CloudSpace, Account) {
        $scope.resetUser = function() {
            // For now, we will grant the new user all permissions. See http://<server>/specifications/Security
            $scope.newUser = {
                name: '', 
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

        $scope.resetUser();
        CloudSpace.listUsers($scope.currentSpace).then(function(result) {
            $scope.cloudSpaceUsers = result;
        });

        Account.listUsers().then(function(result) {
            $scope.accountUsers = result;
        });

        $scope.$watch('cloudSpaceUsers + accountUsers', function() {
            if ($scope.accountUsers && $scope.cloudSpaceUsers) {
                // This should've been _.difference, but it doesn't support predicates   
                $scope.unauthorizedUsers = _.filter($scope.accountUsers, function(user) {
                    return !_.findWhere($scope.cloudSpaceUsers, {id: user.id})
                });
            }
        }, true);

        $scope.userCanBeAdded = function(nameOrEmail) {
            return _.findWhere($scope.unauthorizedUsers, {'name': $scope.newUser.name});
        }

        $scope.addUser = function() {
            if (!$scope.userCanBeAdded($scope.newUser.name))
                return false;

            var newUser = _.findWhere($scope.unauthorizedUsers, {name: $scope.newUser.name});

            $scope.cloudSpaceUsers.push(newUser);
            CloudSpace.addUser($scope.currentSpace, newUser, $scope.newUser.access);
            $scope.resetUser();
            return true;
        };

        $scope.deleteUser = function(space, user) {
            $scope.cloudSpaceUsers.splice($scope.cloudSpaceUsers.indexOf(user), 1);
            $scope.unauthorizedUsers.push(user);
            CloudSpace.deleteUser($scope.currentSpace, user);
        };
    }]);
