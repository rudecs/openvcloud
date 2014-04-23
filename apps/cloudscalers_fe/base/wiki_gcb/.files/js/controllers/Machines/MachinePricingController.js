angular.module('cloudscalers.controllers')
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.cpuMem = 0;
        $scope.storage = 0;
        $scope.archive = 0;
        $scope.location = 0;

        $scope.plans = [
            {name: 'Mothership 1', mem: '512MB', cores: 1,  price: 6,   primary: 10, recommended: false},
            {name: 'Mothership 2', mem: '1GB',   cores: 1,  price: 11,  primary: 10, recommended: true },
            {name: 'Mothership 3', mem: '2GB',   cores: 2,  price: 20,  primary: 10, recommended: false},
            {name: 'Mothership 4', mem: '4GB',   cores: 2,  price: 36,  primary: 10, recommended: false},
            {name: 'Mothership 5', mem: '8GB',   cores: 4,  price: 64,  primary: 10, recommended: false},
            {name: 'Mothership 6', mem: '16GB',  cores: 8,  price: 112, primary: 10, recommended: false},
        ];

    }]);
