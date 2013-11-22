angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', '$window', function($scope, User, Account, CloudSpace, $window) {
        $scope.currentUser = User.current();

        $scope.currentSpace = undefined;


        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });
        
        CloudSpace.list().then(function(cloudspaces){
        	$scope.cloudspaces = cloudspaces;
        });
        
        $scope.$watch('cloudspaces', function(){
        	$scope.currentSpace = _.first($scope.cloudspaces);
        })
        
        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };
        
        
        

        

    }]);
