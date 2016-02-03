angular.module('cloudscalers.controllers')
    .controller('CloudSpaceAccessManagementController', ['$scope', 'CloudSpace', 'Users', '$http','$ErrorResponseAlert','$timeout', '$modal', function($scope, CloudSpace, Users,$http,$ErrorResponseAlert, $timeout, $modal) {

        $scope.shareCloudSpaceMessage = false;
        $scope.accessTypes = CloudSpace.cloudspaceAccessRights();

        function userMessage(message, style, resetUser) {
            if (_.isUndefined(resetUser)) {
                resetUser = true;
            }

            $scope.shareCloudSpaceMessage = true;
            $scope.shareCloudSpaceStyle = style;
            $scope.shareCloudSpaceTxt = message;

            if (resetUser) {
                $scope.resetUser();
            }

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
            if ($scope.currentSpace.acl) {
                var userInAcl = _.find($scope.currentSpace.acl, function(acl) {
                    return acl.userGroupId == $scope.newUser.nameOrEmail; 
                });

                if (userInAcl) {
                    userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
                } else {
                    CloudSpace
                        .addUser($scope.currentSpace, $scope.newUser.nameOrEmail, $scope.newUser.access)
                        .then(function() {
                            userMessage("Assigned access rights successfully to " + $scope.newUser.nameOrEmail , 'success');

                            $scope
                                .loadSpaceAcl()
                                .then(function() {
                                    $scope.resetUser();
                                    $scope.resetSearchQuery();
                                });
                        }, function(reason) {
                            if (reason.status == 404)
                                userMessage($scope.newUser.nameOrEmail + ' not found', 'danger');
                            else
                                $ErrorResponseAlert(reason);
                        });
                }
            }
        };

        $scope.inviteUser = function() {
            var alreadyInvited = _.find($scope.currentSpace.acl, function(acl) {
                return acl.userGroupId == $scope.newUser.nameOrEmail;
            });

            if (alreadyInvited) {
                userMessage($scope.newUser.nameOrEmail + ' already invited', 'danger', false);
                return;
            }
            
            CloudSpace
                .inviteUser($scope.currentSpace, $scope.newUser.nameOrEmail, $scope.newUser.access)
                .then(function() {
                    userMessage('Invitation sent successfully to ' + $scope.newUser.nameOrEmail , 'success');

                    $scope
                        .loadSpaceAcl()
                        .then(function() {
                            $scope.resetUser();
                            $scope.resetSearchQuery();
                        });
                }, function(response) {
                    userMessage(response.data, 'danger', false);                    
                });
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

        function validateEmail(str) {
            // reference: http://stackoverflow.com/questions/46155/validate-email-address-in-javascript
            var re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(str);
        }

        // autocomplete configuration object
        $scope.autocompleteOptions = {
            shadowInput: true,
            highlightFirst: true,
            boldMatches: true,
            delay: 0,
            searchMethod: 'search',
            templateUrl: 'autocomplete-result-template.html',
            onSelect: function(item, event) {
                event && event.preventDefault();
     
                $scope.$apply(function() {
                    $scope.newUser.nameOrEmail = item.value;
                });
            },
            onEnter: function(event, state) {
                if (state.popupOpen === true) {
                    event && event.preventDefault();
                }
            }
        };

        /**
         * Method to get data for autocomplete popup
         * @param {string} query Input value
         * @param {object} deferred "$q.defer()" object
         */
        $scope.emailMode = false;
        $scope.search = function (query, deferred) {
            CloudSpace
                .searchAcl(query)
                .then(function(data) {
                    // format data
                    var results = [];

                    _.each(data, function(item) {
                        results.push({
                            gravatarurl: item.gravatarurl,
                            value: item.username
                        });
                    });

                    // filter: remove existing users from suggestions
                    results = _.filter(results, function(item) {
                        return _.isUndefined(_.find($scope.currentSpace.acl, function(user) {
                            return user.userGroupId == item.value;
                        }));
                    });

                    var emailInvited = _.find($scope.currentSpace.acl, function(user) {
                        return user.userGroupId === query;
                    });

                    if (results.length === 0 && validateEmail(query) && !emailInvited) {
                        results.push({
                            value: query,
                            validEmail: true
                        });
                    } else if (results.length === 0) {
                        if (emailInvited) {
                            results.push({
                                value: '(' + query + ') already invited.',
                                validEmail: false,
                                selectable: false
                            });
                        } else {
                            results.push({
                                value: 'Enter an email to invite...',
                                validEmail: false,
                                selectable: false
                            });
                        }
                    }

                    // resolve the deferred object
                    deferred.resolve({results: results});
                });
        };

        $scope.resetSearchQuery = function() {
            $scope.emailMode = false;
            $scope.searchQuery = '';
        };

        $scope.$watch('searchQuery', function(searchQuery) {
            $scope.newUser.nameOrEmail = searchQuery;

            if (_.isUndefined(searchQuery)) {
                return;
            }

            if(validateEmail(searchQuery)) {
                $scope.emailMode = true;
            } else {
                $scope.emailMode = false;
            }
        });
    }]);
