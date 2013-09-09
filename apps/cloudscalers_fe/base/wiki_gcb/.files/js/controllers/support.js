myAppControllers
    .controller('SupportController', ['$scope', 'SettingsService', function($scope, SettingsService) {
        var settings = SettingsService.getAll();
        if (settings.length == 0) {
            settings = {
                id: 1,
                name: 'User name',
                email: 'email@site.com',
                credit: 50,
                creditHistory: [],
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
    }])
