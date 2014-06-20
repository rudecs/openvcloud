angular.module('cloudscalers.controllers')
    .controller('AuthenticatedSessionController', ['$scope', 'User', 'Account', 'CloudSpace', 'LoadingDialog', '$route', '$window','$timeout', '$location', function($scope, User, Account, CloudSpace, LoadingDialog, $route, $window, $timeout, $location) {
        $scope.currentUser = User.current();
        $scope.currentSpace = CloudSpace.current();
        $scope.currentAccount = $scope.currentSpace ? {id:$scope.currentSpace.accountId, name:$scope.currentSpace.accountName} : {id:''};

        $scope.setCurrentCloudspace = function(space) {
            if (space.locationurl != null){
                var currentlocation = $window.location;
                if (currentlocation.origin != space.locationurl){
                    $window.location = space.locationurl + '/wiki_gcb/SwitchSpace'
                            + '?username=' + encodeURIComponent($scope.currentUser.username)
                            + '&token=' + encodeURIComponent($scope.currentUser.api_key)
                            + '&spaceId=' + encodeURIComponent(space.id);
                    return
                }
            }

            CloudSpace.setCurrent(space);
            $scope.currentSpace = space;
            $scope.setCurrentAccount();
        };

        $scope.setCurrentAccount = function(){
            if ($scope.currentSpace){
                $scope.currentAccount = {id: $scope.currentSpace.accountId, name: $scope.currentSpace.accountName};
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
            if ($scope.currentSpace && _.findWhere($scope.cloudspaces, {id: $scope.currentSpace.id}))
                return;

            $scope.setCurrentCloudspace(_.first($scope.cloudspaces));
        }, true);

        $scope.logout = function() {
            User.logout();

			var uri = new URI($window.location);
			uri.filename('');
			uri.fragment('');
			$window.location = uri.toString();
        };

    }]);
