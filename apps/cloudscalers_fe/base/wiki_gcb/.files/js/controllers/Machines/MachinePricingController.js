angular.module('cloudscalers.controllers')
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.pricingModel = 'mo';

        $scope.$watch('pricingModel', function() {
            if ($scope.pricingModel == 'mo') {
                $scope.linuxPlans = [
                    {name: 'Mothership 1', mem: '512MB', cores: 1,  price: 6,   primary: 10, recommended: false},
                    {name: 'Mothership 2', mem: '1GB',   cores: 1,  price: 11,  primary: 10, recommended: true },
                    {name: 'Mothership 3', mem: '2GB',   cores: 2,  price: 20,  primary: 10, recommended: false},
                    {name: 'Mothership 4', mem: '4GB',   cores: 2,  price: 36,  primary: 10, recommended: false},
                    {name: 'Mothership 5', mem: '8GB',   cores: 4,  price: 64,  primary: 10, recommended: false},
                    {name: 'Mothership 6', mem: '16GB',  cores: 8,  price: 112, primary: 10, recommended: false},
                ];

                $scope.windowsPlans = [
                    {name: 'Mothership 1', mem: '512MB', cores: 1,  price: 12,  primary: 10, recommended: false},
                    {name: 'Mothership 2', mem: '1GB',   cores: 1,  price: 22,  primary: 10, recommended: true },
                    {name: 'Mothership 3', mem: '2GB',   cores: 2,  price: 40,  primary: 10, recommended: false},
                    {name: 'Mothership 4', mem: '4GB',   cores: 2,  price: 72,  primary: 10, recommended: false},
                    {name: 'Mothership 5', mem: '8GB',   cores: 4,  price: 128, primary: 10, recommended: false},
                    {name: 'Mothership 6', mem: '16GB',  cores: 8,  price: 224, primary: 10, recommended: false},
                ];
            } else {
                $scope.linuxPlans = [
                    {name: 'Mothership 1', mem: '512MB', cores: 1,  price: 0.0083,  primary: 10, recommended: false},
                    {name: 'Mothership 2', mem: '1GB',   cores: 1,  price: 0.0153,  primary: 10, recommended: true },
                    {name: 'Mothership 3', mem: '2GB',   cores: 2,  price: 0.0278,  primary: 10, recommended: false},
                    {name: 'Mothership 4', mem: '4GB',   cores: 2,  price: 0.0500,  primary: 10, recommended: false},
                    {name: 'Mothership 5', mem: '8GB',   cores: 4,  price: 0.0889, primary: 10, recommended: false},
                    {name: 'Mothership 6', mem: '16GB',  cores: 8,  price: 0.1556, primary: 10, recommended: false},
                ];

                $scope.windowsPlans = [
                    {name: 'Mothership 1', mem: '512MB', cores: 1,  price: 0.0167,  primary: 10, recommended: false},
                    {name: 'Mothership 2', mem: '1GB',   cores: 1,  price: 0.0306,  primary: 10, recommended: true },
                    {name: 'Mothership 3', mem: '2GB',   cores: 2,  price: 0.0556,  primary: 10, recommended: false},
                    {name: 'Mothership 4', mem: '4GB',   cores: 2,  price: 0.1000,  primary: 10, recommended: false},
                    {name: 'Mothership 5', mem: '8GB',   cores: 4,  price: 0.1778,  primary: 10, recommended: false},
                    {name: 'Mothership 6', mem: '16GB',  cores: 8,  price: 0.3111,  primary: 10, recommended: false},
                ];
            }
        });

    }]);
