angular.module('cloudscalers.controllers')
    .controller('CloudSpaceAccessManagementController', ['$scope', 'CloudSpace', '$ErrorResponseAlert', function($scope, CloudSpace, $ErrorResponseAlert) {
        $scope.resetUser = function() {
            $scope.newUser = {
                nameOrEmail: '', 
                access: {
                    R: true,
                    X: true,
                    C: true,
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
            }, function(reason) {
                if (reason.status == 404)
                    $scope.userError = 'User not found';
                else
                    $ErrorResponseAlert(reason);
            });
        };

        $scope.deleteUser = function(space, user) {
            CloudSpace.deleteUser($scope.currentSpace, user.userGroupId).
            then(function() {
                    $scope.loadSpaceAcl();
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
        };
    }]);
