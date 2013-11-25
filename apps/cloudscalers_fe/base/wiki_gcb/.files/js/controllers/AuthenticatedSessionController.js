angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', '$window', function($scope, User, Account, CloudSpace, $window) {
        $scope.currentUser = User.current();

        $scope.currentSpace = undefined;
        $scope.currentAccount = undefined;

        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });
        
        CloudSpace.list().then(function(cloudspaces){
        	$scope.cloudspaces = cloudspaces;
        });
        
        $scope.$watch('cloudspaces', function(){
        	$scope.setCurrentCloudspace(_.first($scope.cloudspaces));
        })
        
        $scope.setCurrentCloudspace = function(space) {
            $scope.currentSpace = space;
            $scope.setCurrentAccount();
        };
        
        $scope.$watch('accounts', function(){
        	$scope.setCurrentAccount();
        });
        
        $scope.setCurrentAccount = function(){
        	if ($scope.currentSpace && $scope.accounts){
        		$scope.currentAccount = _.findWhere($scope.accounts, {id: $scope.currentSpace.accountId});
        	}
        }
    
        
        $scope.logout = function() {
            User.logout();
            
			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };
        
        
        

        

    }]);
