angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', 'LoadingDialog', '$route', '$window','$timeout', function($scope, User, Account, CloudSpace, LoadingDialog, $route, $window, $timeout) {
        $scope.currentUser = User.current();
        $scope.currentSpace = CloudSpace.current();
        $scope.currentAccount = undefined;

        // Get the user's email
        User.get($scope.currentUser.username)
            .then(function(result) { 
                    $scope.currentUser.email = result.data.emailaddresses.length > 0 ? result.data.emailaddresses[0] : "";
                }, function(result) { 
                    $scope.emailError = result;
                });

        $scope.setCurrentCloudspace = function(space) {
            CloudSpace.setCurrent(space);
            $scope.currentSpace = space;
            $scope.setCurrentAccount();
        };
        
        $scope.setCurrentAccount = function(){
            if ($scope.currentSpace && $scope.accounts){
                $scope.currentAccount = _.findWhere($scope.accounts, {id: $scope.currentSpace.accountId});
            }
        };

        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });

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
            if ($scope.currentSpace && _.findWhere($scope.cloudspaces, {id: $scope.currentSpace.id}))
                return;

            $scope.setCurrentCloudspace(_.first($scope.cloudspaces));
        }, true);
        
        $scope.$watch('accounts', function(){
        	$scope.setCurrentAccount();
        });
        
        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };

    }]);
