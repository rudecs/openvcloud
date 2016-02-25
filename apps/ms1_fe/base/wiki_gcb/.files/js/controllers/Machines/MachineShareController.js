angular.module('cloudscalers.controllers')
    .controller('MachineShareController', ['$scope', 'Machine', '$ErrorResponseAlert', '$timeout', '$modal', 'CloudSpace', function($scope, Machine, $ErrorResponseAlert, $timeout, $modal, CloudSpace) {
        $scope.shareMachineMessage = false;
        $scope.accessTypes = Machine.macineAccessRights();

        $scope.orderUsers = function() {
            $scope.machine.acl = _.sortBy($scope.machine.acl, function(user) {
                return user.userGroupId;
            });
        };

        function userMessage(message, style, resetUser) {
            if (_.isUndefined(resetUser)) {
                resetUser = true;
            }

            $scope.shareMachineMessage = true;
            $scope.shareMachineMessageStyle = style;
            $scope.shareMachineMessageTxt = message;

            if (resetUser) {
                $scope.resetUser();
            }

            $timeout(function () {
                $scope.shareMachineMessage = false;
            }, 3000);
        }

        $scope.resetUser = function() {
            $scope.newUser = {
                nameOrEmail: '',
                access: $scope.accessTypes[0].value
            };
        };

        $scope.resetSearchQuery = function() {
            $scope.emailMode = false;
            $scope.searchQuery = '';
        };

        $scope.resetUser();

        $scope.loadMachineAcl = function() {
            return Machine.get($scope.machine.id).then(function(machine) {
                $scope.machine.acl = machine.acl;
            }, function(reason){
              if(reason.status == 403){
                $scope.machine.acl = {};
              }else{
                $ErrorResponseAlert(reason);
              }
            });
        };

        $scope.addUser = function() {
            if ($scope.machine.acl) {
                var userInAcl = _.find($scope.machine.acl, function(acl) {
                    return acl.userGroupId == $scope.newUser.nameOrEmail;
                });

                if (userInAcl) {
                    userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
                } else {
                    Machine
                        .addUser($scope.machine.id, $scope.newUser.nameOrEmail, $scope.newUser.access)
                        .then(function() {
                            $scope.loadMachineAcl();
                            $scope.orderUsers();
                            $scope.resetSearchQuery();
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

        $scope.inviteUser = function() {
            var alreadyInvited = _.find($scope.machine.acl, function(acl) {
                return acl.userGroupId == $scope.newUser.nameOrEmail;
            });

            if (alreadyInvited) {
                userMessage($scope.newUser.nameOrEmail + ' already invited', 'danger', false);
                return;
            }

            Machine
                .inviteUser($scope.machine.id, $scope.newUser.nameOrEmail, $scope.newUser.access)
                .then(function() {
                    $scope.machine.acl.push({
                        type: 'U',
                        guid: '',
                        right: $scope.newUser.access,
                        userGroupId: $scope.newUser.nameOrEmail,
                        canBeDeleted: true,
                        status: 'INVITED'
                    });

                    $scope.orderUsers();
                    $scope.resetSearchQuery();
                    userMessage('Invitation sent successfully to ' + $scope.newUser.nameOrEmail , 'success');
                }, function(response) {
                    userMessage(response.data, 'danger', false);
                });
        };

        $scope.deleteUser = function(machineId, user, userCanBeDeleted) {
            if(!userCanBeDeleted){
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
                Machine.deleteUser(machineId, user).
                then(function() {
                    $scope.loadMachineAcl();
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
                    $scope.userName = user;
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
                    $scope.loadMachineAcl();
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

                    var emailInvited = _.find($scope.machine.acl, function(user) {
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

        $scope.$watch('machine.acl', function(newVal, oldVal) {
            if (_.isUndefined(newVal)) {
                return;
            }

            if (_.isEqual(newVal, oldVal) === false) {
                $scope.orderUsers();
            }
        });
    }]);
