angular.module('cloudscalers.controllers')
    .controller('AccountSettingsController', ['$scope', 'Account', '$ErrorResponseAlert', '$modal', '$timeout', function($scope, Account, $ErrorResponseAlert, $modal, $timeout) {
      $scope.$watch("currentAccount", function(){
        if($scope.currentAccount){
          $scope.loadAccountAcl();
        }
      });
      $scope.shareAccountMessage = false;
      $scope.accessTypes = Account.accountAccessRights();

      function userMessage(message, style) {
          $scope.shareAccountMessage = true;
          $scope.shareAccountStyle = style;
          $scope.shareAccountTxt = message;
          $scope.resetUser();
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

      $scope.loadAccountAcl = function() {
          return Account.get($scope.currentAccount.id).then(function(account) {
              $scope.currentAccount.userRightsOnAccount = account.acl;
          }, function(reason){
            $ErrorResponseAlert(reason);
          });
      };

      $scope.resetUser();
      $scope.loadAccountAcl();
      $scope.userError = false;

      $scope.addUser = function() {
          if($scope.currentAccount.userRightsOnAccount){
              var userInAcl = _.find($scope.currentAccount.userRightsOnAccount, function(acl) { return acl.userGroupId == $scope.newUser.nameOrEmail; });
              if( userInAcl ){
                  userMessage($scope.newUser.nameOrEmail + " already have access rights.", 'danger');
              }else{
                  Account.addUser($scope.currentAccount.id, $scope.newUser.nameOrEmail, $scope.newUser.access).then(function() {
                      $scope.currentAccount.userRightsOnAccount.push({userGroupId: $scope.newUser.nameOrEmail, right: $scope.newUser.access});
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

      $scope.deleteUser = function(user) {
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
                        var userInACL = _.findWhere($scope.currentAccount.userRightsOnAccount, {userGroupId: user.userGroupId});
                        $scope.currentAccount.userRightsOnAccount.splice([$scope.currentAccount.userRightsOnAccount.indexOf(userInACL)] ,1);
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
              Account.updateUser(currentAccount.accountId, accessRight.user, accessRight.editUserAccess).
              then(function() {
                  var userInACL = _.findWhere($scope.currentAccount.userRightsOnAccount, {userGroupId: accessRight.user});
                  _.findWhere($scope.currentAccount.userRightsOnAccount, {userGroupId: accessRight.user}).right = accessRight.editUserAccess;
                  userMessage("Access right updated successfully for " + user , 'success');
                  $scope.resetUser();
              },
              function(reason){
                  $ErrorResponseAlert(reason);
              });
          });
      };
    }]);
