angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', 'LoadingDialog', '$route', '$window','$timeout', '$location', function($scope, User, Account, CloudSpace, LoadingDialog, $route, $window, $timeout, $location) {
        $scope.currentUser = User.current();
        $scope.currentSpace = CloudSpace.current();
        $scope.currentAccount = $scope.currentSpace ? {id:$scope.currentSpace.accountId, name:$scope.currentSpace.accountName, userRightsOnAccount: $scope.currentSpace.acl, userRightsOnAccountBilling: $scope.currentSpace.userRightsOnAccountBilling} : {id:''};

        $scope.setCurrentCloudspace = function(space) {
        	if (space == null)
        	{
        		return;
        	}

            CloudSpace.setCurrent(space);
            $scope.currentSpace = space;
            $scope.setCurrentAccount();
        };

        $scope.setCurrentAccount = function(){
            if ($scope.currentSpace){
                $scope.currentAccount = {id: $scope.currentSpace.accountId, name: $scope.currentSpace.accountName, userRightsOnAccount: $scope.currentSpace.acl, userRightsOnAccountBilling: $scope.currentSpace.userRightsOnAccountBilling};
            }
        };

        $scope.loadSpaces = function() {
            return CloudSpace.list().then(function(cloudspaces){
                $scope.cloudspaces = cloudspaces;
                return cloudspaces;
            });
        };

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

	    $scope.$watch('currentAccount',  function(){
              if($scope.currentAccount){
                    $scope.userRightsOnAccountBilling = $scope.currentAccount.userRightsOnAccountBilling;
	          }
            }, true);

        $scope.logout = function() {
            User.logout();

			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };

        $scope.$watch('currentSpace', function () {
            CloudSpace.get($scope.currentSpace.id).then(function (data) {
                if($scope.currentSpace.acl.length != data.acl.length){
                    $scope.currentSpace.acl = data.acl;
                }
            });
            if($scope.currentUser.username && $scope.currentSpace.acl){
                var currentUserAccessright =  _.find($scope.currentSpace.acl , function(acl) { return acl.userGroupId == $scope.currentUser.username; })
                if(currentUserAccessright){
                    currentUserAccessright = currentUserAccessright.right.toUpperCase();
                    if(currentUserAccessright == "R"){
                        $scope.currentUserAccessrightOnCloudSpace = 'Read';
                    }else if( currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') == -1 && currentUserAccessright.indexOf('U') == -1){
                        $scope.currentUserAccessrightOnCloudSpace = "ReadWrite";
                    }else if(currentUserAccessright.indexOf('R') != -1 && currentUserAccessright.indexOf('C') != -1 && currentUserAccessright.indexOf('X') != -1 && currentUserAccessright.indexOf('D') != -1 && currentUserAccessright.indexOf('U') != -1){
                        $scope.currentUserAccessrightOnCloudSpace = "Admin";
                    }
                }
            }
        });

    }]);
