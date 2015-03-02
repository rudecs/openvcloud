angular.module('cloudscalers.controllers')
    .controller('MachineShareController', ['$scope', 'Machine', '$ErrorResponseAlert', '$timeout', '$modal', function($scope, Machine, $ErrorResponseAlert, $timeout, $modal) {
        
        $scope.currentUserIsAdmin = true;

        $scope.$watch('machine.acl', function () {
            if($scope.currentUser.username && $scope.machine.acl){
                var currentUserAccessright =  _.find($scope.machine.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; }).right.toUpperCase();
                // if user isn't admin
                if(currentUserAccessright.indexOf('U') == -1 && currentUserAccessright.indexOf('D') == -1){
                    $scope.currentUserIsAdmin = false;
                }
            }
        });

        $scope.shareMachineMessage = false;
        $scope.accessTypes = Machine.macineAccessRights();

        function userMessage(message, style) {
            $scope.shareMachineMessage = true;
            $scope.shareMachineMessageStyle = style;
            $scope.shareMachineMessageTxt = message;
            $scope.resetUser();
            $timeout(function () {
                $scope.shareMachineMessage = false;
            }, 3000);
        }

        $scope.resetUser = function() {
            $scope.newUser = { nameOrEmail: '', access: $scope.accessTypes[0].value };
        };

        $scope.resetUser();

        $scope.addUser = function() {
            if($scope.machine.acl){
                var userInAcl = _.find($scope.machine.acl, function(acl) { return acl.userGroupId == $scope.newUser.nameOrEmail; });
                if( userInAcl ){
                    userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
                }else{
                    Machine.addUser($scope.machine.id, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                        $scope.machine.acl.push({ type: 'U', guid: '', right: $scope.newUser.access, userGroupId: $scope.newUser.nameOrEmail });
                        userMessage("Assigned access rights successfully to " + $scope.newUser.nameOrEmail , 'success');
                    }, function(reason) {
                        if (reason.status == 404)
                            userMessage($scope.newUser.nameOrEmail + ' not found', 'danger');
                        else
                            $ErrorResponseAlert(reason);
                    });
                }
            }
        };

        $scope.deleteUser = function(machineId, user) {
            var modalInstance = $modal.open({
                templateUrl: 'deleteUserDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.ok = function () {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelRemoveUser = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });

            modalInstance.result.then(function (result) {
                Machine.deleteUser(machineId, user).
                then(function() {
                    $scope.machine.acl.splice(_.where($scope.machine.acl, {userGroupId: user}), 1);
                    userMessage("Assigned access right removed successfully for " + user , 'success');
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
            });
        };

        $scope.loadEditUser = function(machineId, user, right) {
            var modalInstance = $modal.open({
                templateUrl: 'editUserDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.accessTypes = Machine.macineAccessRights();
                    $scope.editUserAccess = right;
                    $scope.changeAccessRight = function(accessRight) {
                        $scope.editUserAccess = accessRight.value;
                    };
                    $scope.ok = function (editUserAccess) {
                        $modalInstance.close({
                            machineId: machineId,
                            user: user,
                            editUserAccess: editUserAccess
                        });
                    };
                    $scope.cancelEditUser = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });
            modalInstance.result.then(function (accessRight) {
                Machine.updateUser(accessRight.machineId, accessRight.user, accessRight.editUserAccess).
                then(function() {
                    var userAcl = _.find($scope.machine.acl , function(acl) { return acl.userGroupId == accessRight.user; });
                    $scope.machine.acl[$scope.machine.acl.indexOf(userAcl)].right = accessRight.editUserAccess;
                    userMessage("Access right updated successfully for " + user , 'success');
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
            });
        };
        
    }]);
