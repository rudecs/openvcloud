angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', 'LoadingDialog', '$route', '$window','$timeout', '$location', 'ipCookie', '$ErrorResponseAlert', '$modal', 'SessionData', function($scope, User, Account, CloudSpace, LoadingDialog, $route, $window, $timeout, $location, ipCookie, $ErrorResponseAlert, $modal, SessionData) {

        $scope.noAccount = false;
        var portal_session_cookie = ipCookie("beaker.session.id");
        if(portal_session_cookie){
            if(!User.current() || User.current().api_key != portal_session_cookie){
                User.getPortalLoggedinUser().then(function(username) {
                    if(username != "guest"){
                        autoLogin(username);
                    }
                },
                function(reason){
                    $scope.login_error = reason.status
                });

            }else{
                autoLogin(User.current().username);
            }
        }

        function setInitialAccount() {
          if($scope.currentSpace){
            $scope.currentAccount = $scope.currentSpace ? {id:$scope.currentSpace.accountId, name:$scope.currentSpace.accountName, userRightsOnCloudspace: $scope.currentSpace.acl, userRightsOnAccountBilling: $scope.currentSpace.userRightsOnAccountBilling} : {id:''};
          }
        };

        function autoLogin(username) {
            User.portalLogin(username, portal_session_cookie);
            $scope.currentUser = User.current();
            $scope.currentUser.acl = {account: 0, cloudspace: 0, machine: 0};
            $scope.currentSpace = CloudSpace.current();
            setInitialAccount();
        };


        $scope.setCurrentCloudspace = function(space) {
        	if (space == null){
        		return;
        	}
          CloudSpace.setCurrent(space);
          $scope.currentSpace = space;
          $scope.setCurrentAccount($scope.currentSpace.accountId);
        };

        $scope.setCurrentAccount = function(currentAccountId){
            $scope.currentAccount.userRightsOnAccount = {};
            if($scope.currentAccount.id){
                Account.get(currentAccountId).then(function(account) {
                    $scope.currentAccount = account;
                    $scope.currentAccount.userRightsOnAccount = account.acl;
                }, function(reason){
                  if(reason.status === 403){
                    $scope.currentUser.acl.account = 0;
                    setInitialAccount();
                  }else{
                    $ErrorResponseAlert(reason);
                  }
                });
            }
        };

        $scope.loadSpaces = function() {
            return CloudSpace.list().then(function(cloudspaces){
                $scope.cloudspaces = cloudspaces;
                if(cloudspaces.length == 0){
                    $timeout(function(){
                        $scope.noAccount = true;
                        SessionData.setSpace();
                    });
                }
                return cloudspaces;
            }, function(reason){
                $ErrorResponseAlert(reason);
            });
        };

        $scope.invalidAccount = function() {
            $window.location = "/";
        }

        $scope.loadSpaces();

        $scope.$watch('cloudspaces', function(){
            if (!$scope.cloudspaces)
                return;

            var currentCloudSpaceFromList;
            if ($scope.currentSpace){
                currentCloudSpaceFromList = _.find($scope.cloudspaces, function(cloudspace){ return cloudspace.id == $scope.currentSpace.id; });
            }
            if (currentCloudSpaceFromList == null){
                currentCloudSpaceFromList = _.first($scope.cloudspaces);
            }
            $scope.setCurrentCloudspace(currentCloudSpaceFromList);

        }, true);

        $scope.getUserAccessOnAccount = function(){
          if($scope.currentAccount.userRightsOnAccount){
            var userInCurrentAccount = _.find($scope.currentAccount.userRightsOnAccount , function(acl) { return acl.userGroupId == $scope.currentUser.username; });
            $scope.currentUser.acl.account = 0;
              if(userInCurrentAccount){
                  var currentUserAccessrightOnAccount = userInCurrentAccount.right.toUpperCase();
                  if(currentUserAccessrightOnAccount == "R"){
                      $scope.currentUser.acl.account = 1;
                  }else if(currentUserAccessrightOnAccount.search(/R|C|X/) != -1 && currentUserAccessrightOnAccount.search(/D|U/) == -1){
                    $scope.currentUser.acl.account = 2;
                  }else if(currentUserAccessrightOnAccount.search(/R|C|X|D|U/) != -1 ){
                      $scope.currentUser.acl.account = 3;
                  }
              }
          }
        };

	      $scope.$watch('currentAccount.id + currentAccount.userRightsOnAccount',  function(){
          if($scope.currentAccount){
            $scope.getUserAccessOnAccount();
          }
        });

        $scope.logout = function() {
            User.logout();
      			var uri = new URI($window.location);
      			uri.filename('');
      			uri.fragment('');
      			$window.location = uri.toString();
        };

        $scope.$watch('currentSpace', function () {
            if($scope.currentSpace && $scope.currentUser){
                CloudSpace.get($scope.currentSpace.id).then(function (data) {
                    if($scope.currentSpace.acl.length != data.acl.length){
                        $scope.currentSpace.acl = data.acl;
                    }
                    $scope.setCurrentAccount($scope.currentSpace.accountId);
                },function(reason) {
                  if(reason.status === 403){
                    $scope.currentUser.acl.cloudspace = 0;
                  }
                });
                if($scope.currentUser.username && $scope.currentSpace.acl){
                    var currentUserAccessright =  _.find($scope.currentSpace.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; })
                    if(currentUserAccessright){
                        currentUserAccessright = currentUserAccessright.right.toUpperCase();
                        if(currentUserAccessright == "R"){
                            $scope.currentUser.acl.cloudspace = 1;
                        }else if( currentUserAccessright.search(/R|C|X/) != -1 && currentUserAccessright.search(/D|U/) == -1 ){
                            $scope.currentUser.acl.cloudspace = 2;
                        }else if( currentUserAccessright.search(/R|C|X|D|U/) != -1 ){
                            $scope.currentUser.acl.cloudspace = 3;
                        }
                    }
                }
              $scope.getUserAccessOnAccount();
            }
        });

}]);
