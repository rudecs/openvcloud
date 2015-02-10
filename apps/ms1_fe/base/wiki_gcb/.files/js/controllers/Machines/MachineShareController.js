angular.module('cloudscalers.controllers')
    .controller('MachineShareController', ['$scope', 'Machine', '$ErrorResponseAlert', function($scope, Machine, $ErrorResponseAlert) {
        
        // apply machine access rights on machine operations, other?
        // if user alredy have access right, need to check before insert?

        $scope.accessTypes = [
            {
              name: 'Read',
              value: 'R'
            }, 
            {
              name: 'Read/Write',
              value: 'RCX'
            },
            {
              name: 'Admin',
              value: 'RCADUX'
            }
        ];

        $scope.resetUser = function() {
            $scope.newUser = { nameOrEmail: '', access: $scope.accessTypes[0].value };
        };

        // $scope.loadMachineAcl = function() {
        //     $scope.$watch('machine', function() {
        //         if($scope.machine.acl){
        //             console.log($scope.machine.acl);
        //         }
        //     }, true);
        // };

        $scope.resetUser();
        // $scope.loadMachineAcl();
        $scope.userError = false;

        $scope.addUser = function() {
            $scope.$watch('machine', function() {
                if($scope.machine.acl){
                    if(_.find($scope.machine.acl, function(acl) { return acl.userGroupId == $scope.newUser.nameOrEmail; })){
                        $ErrorResponseAlert('duplicated');
                    }else{
                        console.log('new');
                    }

                    // return Machine.addUser($scope.machine.id, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                    //     // $scope.loadMachineAcl().then(function() {
                    //     // });
                    //     $scope.userError = false;
                    //     $scope.machine.acl.push({ type: 'U', guid: '', right: $scope.newUser.access, userGroupId: $scope.newUser.nameOrEmail });
                    //     console.log($scope.machine.acl, $scope.newUser.nameOrEmail);
                    //     $scope.resetUser();
                    // }, function(reason) {
                    //     if (reason.status == 404)
                    //         $scope.userError = 'User not found';
                    //     else
                    //         $ErrorResponseAlert(reason);
                    // });
                }
            
            }, true);
        };

        $scope.deleteUser = function(space, user) {
            Machine.deleteUser($scope.currentSpace, user.userGroupId).
            then(function() {
                    $scope.loadMachineAcl();
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
        };
    }]);
