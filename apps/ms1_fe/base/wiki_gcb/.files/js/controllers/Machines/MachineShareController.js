angular.module('cloudscalers.controllers')
    .controller('MachineShareController', ['$scope', 'Machine', '$ErrorResponseAlert', '$timeout', '$modal', function($scope, Machine, $ErrorResponseAlert, $timeout, $modal) {
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
                    $scope.editUserAccess = "";
                    $timeout(function () {
                        $scope.$apply(function () {
                            $scope.editUserAccess = right;
                        });
                    }, 5);
                    $scope.userName = user;

                    $scope.ok = function (editUserAccess) {
                        $modalInstance.close('ok');
                    };
                    $scope.cancelEditUser = function () {
                        $modalInstance.dismiss('cancel');
                    };
                },
                resolve: {
                }
            });
            modalInstance.result.then(function (result) {
                // Finalize edit here
                // Machine.updateUser(machineId, user, editUserAccess).
                // then(function() {
                //     console.log($scope.machine);
                //     // console.log($scope.machine.acl[_.where($scope.machine.acl, {userGroupId: user})]);
                // },
                // function(reason){
                //     $ErrorResponseAlert(reason);
                // });
            });
        };
        
    }]);
