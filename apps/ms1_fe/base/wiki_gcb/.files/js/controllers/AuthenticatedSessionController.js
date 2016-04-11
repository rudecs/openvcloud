(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', AuthenticatedSessionController);

  function AuthenticatedSessionController($scope, User, Account, CloudSpace, LoadingDialog,
    $route, $window, $timeout, $location, ipCookie, $ErrorResponseAlert, $modal, SessionData) {

    $scope.setCurrentCloudspace = setCurrentCloudspace;
    $scope.checkDisabledAccount = checkDisabledAccount;
    $scope.setCurrentAccount = setCurrentAccount;
    $scope.loadSpaces = loadSpaces;
    $scope.invalidAccount = invalidAccount;
    $scope.getUserAccessOnAccount = getUserAccessOnAccount;
    $scope.logout = logout;
    $scope.noAccount = false;
    var portalSessionCookie = ipCookie('beaker.session.id');

    // Binding and Watch
    $scope.$watch('cloudspaces', cloudspaces, true);
    $scope.$watch('currentAccount.id + currentAccount.userRightsOnAccount', CurrentAccountIdAndUserRights);
    $scope.$watch('currentSpace', currentSpace);

    // Initialization: Functions invokation logic
    checkUserAccountAccessibility();
    $scope.loadSpaces();

    // Functions
    function checkUserAccountAccessibility() {
      if (portalSessionCookie) {
        if (!User.current() || User.current().api_key !== portalSessionCookie) {
          User.getPortalLoggedinUser().then(function(username) {
            if (username !== 'guest') {
              autoLogin(username);
            }
          }, function(reason) {
            $scope.loginError = reason.status;
          });

        }else {
          autoLogin(User.current().username);
        }
      }
    }

    function setInitialAccount() {
      // Else 'won't happen' and Must be refactored, $scope.currentAccount will always exist
      if ($scope.currentSpace) {
        $scope.currentAccount = {
          id: $scope.currentSpace.accountId,
          name: $scope.currentSpace.accountName,
          userRightsOnCloudspace: $scope.currentSpace.acl,
          userRightsOnAccountBilling: $scope.currentSpace.userRightsOnAccountBilling
        };
      }else {
        $scope.currentAccount = {id: ''};
      }
    }

    function autoLogin(username) {
      User.portalLogin(username, portalSessionCookie);
      $scope.currentUser = User.current();
      $scope.currentUser.acl = {account: 0, cloudspace: 0, machine: 0};
      $scope.currentSpace = CloudSpace.current();
      setInitialAccount();
    }
    function setCurrentCloudspace(space) {
      if (space === null) {
        return;
      }
      CloudSpace.setCurrent(space);
      $scope.currentSpace = space;
      $scope.setCurrentAccount($scope.currentSpace.accountId);
    }
    function checkDisabledAccount(status) {
      $scope.visibility = 'show';
      if (status === 'DISABLED') {
        _.each($scope.currentUser.acl ,function(value, key) {
          $scope.currentUser.acl[key] = 1;
        });
      }
    }
    function setCurrentAccount(currentAccountId) {
      $scope.currentAccount.userRightsOnAccount = {};
      if ($scope.currentAccount.id) {
        Account.get(currentAccountId).then(function(account) {
          $scope.currentAccount = account;
          $scope.currentAccount.userRightsOnAccount = account.acl;
          $scope.checkDisabledAccount(account.status);
        }, function(reason) {
          if (reason.status === 403) {
            $scope.currentUser.acl.account = 0;
            setInitialAccount();
          }else {
            $ErrorResponseAlert(reason);
          }
        });
      }
    }
    function loadSpaces() {
      return CloudSpace.list().then(function(cloudspaces) {
        $scope.cloudspaces = cloudspaces;
        if (cloudspaces.length === 0) {
          $timeout(function() {
            $scope.noAccount = true;
            SessionData.setSpace();
          });
        }
        return cloudspaces;
      }, function(reason) {
        $ErrorResponseAlert(reason);
      });
    }
    function invalidAccount() {
      $window.location = '/';
    }
    function cloudspaces() {
      if (!$scope.cloudspaces) {return;}

      var currentCloudSpaceFromList;
      if ($scope.currentSpace) {
        currentCloudSpaceFromList = _.find($scope.cloudspaces, function(cloudspace) {
          return cloudspace.id === $scope.currentSpace.id;
        });
      }
      if (currentCloudSpaceFromList === null) {
        currentCloudSpaceFromList = _.first($scope.cloudspaces);
      }
      $scope.setCurrentCloudspace(currentCloudSpaceFromList);
    }
    function getUserAccessOnAccount() {
      if ($scope.currentAccount.userRightsOnAccount) {
        var userInCurrentAccount = _.find($scope.currentAccount.userRightsOnAccount , function(acl) {
          return acl.userGroupId === $scope.currentUser.username;
        });
        $scope.currentUser.acl.account = 0;
        if (userInCurrentAccount) {
          var currentUserAccessrightOnAccount = userInCurrentAccount.right.toUpperCase();
          if (currentUserAccessrightOnAccount === 'R') {
            $scope.currentUser.acl.account = 1;
          }else if (currentUserAccessrightOnAccount.search(/R|C|X/) !== -1 &&
            currentUserAccessrightOnAccount.search(/D|U/) === -1) {
            $scope.currentUser.acl.account = 2;
          }else if (currentUserAccessrightOnAccount.search(/R|C|X|D|U/) !== -1) {
            $scope.currentUser.acl.account = 3;
          }
        }
      }
    }
    function CurrentAccountIdAndUserRights() {
      if ($scope.currentAccount && $scope.currentAccount.status !== 'DISABLED') {
        $scope.getUserAccessOnAccount();
      }
    }
    function logout() {
      User.logout();
      var uri = new URI($window.location);
      uri.filename('');
      uri.fragment('');
      $window.location = uri.toString();
    }
    function currentSpace() {
      if ($scope.currentSpace && $scope.currentUser) {
        CloudSpace.get($scope.currentSpace.id).then(function(data) {
          if ($scope.currentSpace.acl.length !== data.acl.length) {
            $scope.currentSpace.acl = data.acl;
          }
          $scope.setCurrentAccount($scope.currentSpace.accountId);
        },function(reason) {
                if (reason.status === 403) {
                  $scope.currentUser.acl.cloudspace = 0;
                }
              });
        if ($scope.currentUser.username && $scope.currentSpace.acl) {
          var currentUserAccessright = _.find($scope.currentSpace.acl , function(acl) {
            return acl.userGroupId === $scope.currentUser.username;
          });
          if (currentUserAccessright) {
            currentUserAccessright = currentUserAccessright.right.toUpperCase();
            if (currentUserAccessright === 'R') {
              $scope.currentUser.acl.cloudspace = 1;
            }else if (currentUserAccessright.search(/R|C|X/) !== -1 && currentUserAccessright.search(/D|U/) === -1) {
              $scope.currentUser.acl.cloudspace = 2;
            }else if (currentUserAccessright.search(/R|C|X|D|U/) !== -1) {
              $scope.currentUser.acl.cloudspace = 3;
            }
          }
        }
        $scope.getUserAccessOnAccount();
      }
    }
  }
})();
