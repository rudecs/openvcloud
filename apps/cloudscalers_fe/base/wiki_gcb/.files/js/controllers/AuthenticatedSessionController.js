angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'APIKey', 'Account', 'CloudSpace', function($scope, User, APIKey, Account, CloudSpace) {
        $scope.user = User.current();

        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });
        
        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			$window.location = uri.toString();
        };
        
        
        

        

    }]);
