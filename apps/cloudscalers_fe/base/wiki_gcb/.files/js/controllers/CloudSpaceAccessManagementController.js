angular.module('cloudscalers.controllers')
    .controller('CloudSpaceAccessManagementController', ['$scope', 'CloudSpace', function($scope, CloudSpace) {
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
            return CloudSpace.get($scope.currentSpace.id).then(function(space) {
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
                if (result.status == 404)
                    $scope.userError = 'User not found';
                else
                    $scope.userError = 'An error has occurred';
            });
        };

        $scope.deleteUser = function(space, user) {
            CloudSpace.deleteUser($scope.currentSpace, user.userGroupId).then(function() {
                $scope.loadSpaceAcl();
            });
        };
    }]);
