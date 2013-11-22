angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'APIKey', 'Account', 'CloudSpace', '$window', function($scope, User, APIKey, Account, CloudSpace, $window) {
        //$scope.user = User.current();
        

        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });
        
//        CloudSpace.list().then(function(cloudspaces){
//        	$scope.cloudspaces = cloudspaces;
//        });
        
        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };
        
        
        

        

    }]);
