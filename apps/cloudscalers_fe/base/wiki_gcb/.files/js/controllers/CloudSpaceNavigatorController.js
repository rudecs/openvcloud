
cloudscalersControllers
    .controller('CloudSpaceNavigatorController', ['$scope', 'Account', function($scope, Account) {
        $scope.isCollapsed = true;
        $scope.currentSpace = 'Account/Space';

        Account.list().then(function(accounts) {
            $scope.accounts = accounts;
        });

        $scope.setCurrentCloudspace = function(accountName, spaceName) {
            $scope.currentSpace = accountName + '/' + spaceName;
        };
    }]);
