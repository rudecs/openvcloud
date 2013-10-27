cloudscalersControllers
    .controller('BillingController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: 'User name',
                email: 'email@site.com',
                credit: 50,
                creditHistory: [],
                addedAmount: 0,
                // password: '', // Passwords must not be saved locally
                //ccType: '',
                //ccNum: '',
                //ccExpiration: '',
                //ccv: ''
            };
        } else {
            settings = settings[0];
        }
        $scope.settings = settings;
        $scope.addedAmount = 0;

        $scope.add = function() {
            if (!$scope.addedAmount || $scope.addedAmount <= 0)
                return;
            $scope.settings.credit += $scope.addedAmount;
            $scope.settings.creditHistory.push({date: getFormattedDate(), description: 'Payment', amount: $scope.addedAmount});
            SettingsService.save($scope.settings);
            showLoading('Adding credit');
        };
    }]);