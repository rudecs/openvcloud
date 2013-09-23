cloudscalersControllers
    .controller('SettingsController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: '',
                email: '',
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

        $scope.save = function() {
            $scope.settings.password = $scope.password;
            $scope.settings.ccNum = $scope.ccNum;
            $scope.settings.ccType = $scope.ccType;
            $scope.settings.ccExpiration = $scope.ccExpiration;
            $scope.settings.ccv = $scope.ccv;

            SettingsService.save($scope.settings);
        }
    }])