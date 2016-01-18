angular.module('cloudscalers.controllers')
    .controller('CloudSpaceAccessManagementController', ['$scope', 'CloudSpace', 'Users', '$http','$ErrorResponseAlert','$timeout', '$modal', function($scope, CloudSpace, Users,$http,$ErrorResponseAlert, $timeout, $modal) {

        $scope.shareCloudSpaceMessage = false;
        $scope.accessTypes = CloudSpace.cloudspaceAccessRights();

        function userMessage(message, style) {
            $scope.shareCloudSpaceMessage = true;
            $scope.shareCloudSpaceStyle = style;
            $scope.shareCloudSpaceTxt = message;
            $scope.resetUser();
            $timeout(function () {
                $scope.shareCloudSpaceMessage = false;
            }, 3000);
        }

        $scope.resetUser = function() {
            $scope.newUser = {
                nameOrEmail: '',
                access: $scope.accessTypes[0].value
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
            if($scope.currentSpace.acl){
                var userInAcl = _.find($scope.currentSpace.acl, function(acl) { return acl.userGroupId == $scope.newUser.nameOrEmail; });
                if( userInAcl ){
                    userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
                }else{
                    CloudSpace.addUser($scope.currentSpace, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                        $scope.loadSpaceAcl().then(function() {
                            $scope.resetUser();
                        });
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

        $scope.deleteUser = function(space, user) {
            if(user.canBeDeleted != true){
              return false;
            }
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
                CloudSpace.deleteUser($scope.currentSpace, user.userGroupId).
                    then(function() {
                        $scope.loadSpaceAcl();
                        $scope.currentSpace.acl.splice(_.indexOf($scope.currentSpace.acl, {userGroupId: user.userGroupId}), 1);
                        userMessage("Assigned access right removed successfully for " + user.userGroupId , 'success');
                    },
                    function(reason){
                        $ErrorResponseAlert(reason);
                    });
            });
        };

        $scope.loadEditUser = function(currentSpace, user, right) {
            var modalInstance = $modal.open({
                templateUrl: 'editUserDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.accessTypes = CloudSpace.cloudspaceAccessRights();
                    $scope.editUserAccess = right;
                    $scope.userName = user;
                    $scope.changeAccessRight = function(accessRight) {
                        $scope.editUserAccess = accessRight.value;
                    };
                    $scope.ok = function (editUserAccess) {
                        $modalInstance.close({
                            currentSpaceId: currentSpace.id,
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
                CloudSpace.updateUser(accessRight.currentSpaceId, accessRight.user, accessRight.editUserAccess).
                then(function() {
                    $scope.loadSpaceAcl().then(function() {
                        $scope.resetUser();
                    });
                    userMessage("Access right updated successfully for " + user , 'success');
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
            });
        };

  			$scope.search = function (query, deferred){
          // TODO add autocomplete function
  				// $http.get(cloudspaceconfig.apibaseurl + '/users/getMatchingUsernames?limit=5&usernameregex=k').success((function (deferred, data) {
  				// 	var results = [];
  				// 	data.forEach(function (item) {
  				// 		results.push({
  				// 			value: item.username,
  				// 			userGravatar: item.gravatarurl
  				// 		});
  				// 	});
  				// 	deferred.resolve({results: results});
  				// }).bind(this, deferred));
  			};
    }]);
