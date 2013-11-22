
angular.module('cloudscalers.controllers')
    .controller('CloudSpaceNavigatorController', ['$scope', 'Account', function($scope, Account) {
        $scope.isCollapsed = true;
        $scope.currentSpace = 'Account/Space';

        $scope.setCurrentCloudspace = function(accountName, spaceName) {
            $scope.currentSpace = accountName + '/' + spaceName;
        };
    }]);
