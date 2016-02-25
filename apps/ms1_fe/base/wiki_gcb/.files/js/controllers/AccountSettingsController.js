angular.module('cloudscalers.controllers')
    .controller('AccountSettingsController', ['$scope', 'Account', '$ErrorResponseAlert', '$modal', '$timeout', 'CloudSpace', function($scope, Account, $ErrorResponseAlert, $modal, $timeout, CloudSpace) {

        $scope.$watch("currentAccount", function(){
          if($scope.currentAccount){
            $scope.loadAccountAcl();
          }
        });

        $scope.shareAccountMessage = false;
        $scope.accessTypes = Account.accountAccessRights();

        function userMessage(message, style, resetUser) {
            if (_.isUndefined(resetUser)) {
              resetUser = true;
            }

            $scope.shareAccountMessage = true;
            $scope.shareAccountStyle = style;
            $scope.shareAccountTxt = message;

            if (resetUser) {
              $scope.resetUser();
            }

            $timeout(function () {
                $scope.shareAccountMessage = false;
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

        $scope.loadAccountAcl = function() {
            return Account.get($scope.currentAccount.id).then(function(account) {
                $scope.currentAccount.userRightsOnAccount = account.acl;
            }, function(reason){
              if(reason.status == 403){
                $scope.currentAccount.userRightsOnAccount = {};
              }else{
                $ErrorResponseAlert(reason);
              }
            });
        };

        $scope.resetUser();
        $scope.userError = false;

        $scope.addUser = function() {
            if($scope.currentAccount.userRightsOnAccount){
                var userInAcl = _.find($scope.currentAccount.userRightsOnAccount, function(acl) { return acl.userGroupId == $scope.newUser.nameOrEmail; });
                if( userInAcl ){
                    userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
                }else{
                    Account.addUser($scope.currentAccount.id, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                        $scope.loadAccountAcl();
                        userMessage("Assigned access rights successfully to " + $scope.newUser.nameOrEmail , 'success');
                        $scope.resetUser();
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
            var alreadyInvited = _.find($scope.currentAccount.userRightsOnAccount, function(user) {
                return user.userGroupId == $scope.newUser.nameOrEmail;
            });

            if (alreadyInvited) {
                userMessage($scope.newUser.nameOrEmail + ' already invited', 'danger', false);
                return;
            }

            Account
                .inviteUser($scope.currentAccount.id, $scope.newUser.nameOrEmail, $scope.newUser.access)
                .then(function() {
                    $scope.currentAccount.userRightsOnAccount.push({
                        right: $scope.newUser.access,
                        userGroupId: $scope.newUser.nameOrEmail,
                        //canBeDeleted: true,
                        status: 'INVITED'
                    });

                    $scope.orderUsers();
                    $scope.resetSearchQuery();
                    userMessage('Invitation sent successfully to ' + $scope.newUser.nameOrEmail , 'success');
                }, function(response) {
                    userMessage(response.data, 'danger', false);
                });
        };

        $scope.deleteUser = function(user) {
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
                Account.deleteUser($scope.currentAccount.id, user.userGroupId).
                    then(function(data) {
                        if(data === "true"){
                          $scope.loadAccountAcl();
                          $scope.resetUser();
                          userMessage("Assigned access right removed successfully for " + user.userGroupId , 'success');
                        }else if(data === "false"){
                          userMessage("Last admin for account can not be deleted " , 'danger');
                        }
                    },
                    function(reason){
                        $ErrorResponseAlert(reason);
                    });
            });
        };

        $scope.loadEditUser = function(currentAccount, user, right) {
            var modalInstance = $modal.open({
                templateUrl: 'editUserDialog.html',
                controller: function($scope, $modalInstance){
                    $scope.accessTypes = Account.accountAccessRights();
                    $scope.editUserAccess = right;
                    $scope.userName = user;
                    $scope.changeAccessRight = function(accessRight) {
                        $scope.editUserAccess = accessRight.value;
                    };
                    $scope.ok = function (editUserAccess) {
                        $modalInstance.close({
                            currentAccountId: currentAccount.id,
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
                Account.updateUser(currentAccount.id, accessRight.user, accessRight.editUserAccess).
                then(function() {
                    $scope.loadAccountAcl();
                    userMessage("Access right updated successfully for " + user , 'success');
                    $scope.resetUser();
                },
                function(reason){
                    $ErrorResponseAlert(reason);
                });
            });
        };

        $scope.orderUsers = function() {
            $scope.currentAccount.userRightsOnAccount = _.sortBy($scope.currentAccount.userRightsOnAccount, function(user) {
                return user.userGroupId;
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
                        return _.isUndefined(_.find($scope.currentAccount.userRightsOnAccount, function(user) {
                            return user.userGroupId == item.value;
                        }));
                    });

                    var emailInvited = _.find($scope.currentAccount.userRightsOnAccount, function(user) {
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

        $scope.$watch('currentAccount.userRightsOnAccount', function(newVal, oldVal) {
            if (_.isUndefined(newVal)) {
                return;
            }

            if (_.isEqual(newVal, oldVal) === false) {
                $scope.orderUsers();
            }
        })
    }]);
