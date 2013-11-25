angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', '$window', function($scope, User, Account, CloudSpace, $window) {
        $scope.currentUser = User.current();
        $scope.currentSpace = CloudSpace.current();    
        $scope.currentAccount = undefined;    
        
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
        
        CloudSpace.list().then(function(cloudspaces){
        	$scope.cloudspaces = cloudspaces;
        });
        
        $scope.$watch('cloudspaces', function(){
            if (!$scope.currentSpace && $scope.cloudspaces)
            	$scope.setCurrentCloudspace(_.first($scope.cloudspaces));
        });
        
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
