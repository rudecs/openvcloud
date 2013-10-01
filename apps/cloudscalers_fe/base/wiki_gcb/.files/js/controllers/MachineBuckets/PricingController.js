cloudscalersControllers
    .controller('PricingController', ['$scope', function($scope) {
        $scope.cpuMem = 0;
        $scope.storage = 0;

        $scope.cpuMemList = [
            {mem: '512MB', cores: 1, price: 5},
            {mem: '1GB', cores: 1, price: 10},
            {mem: '2GB', cores: 2, price: 20},
            {mem: '4GB', cores: 2, price: 40},
            {mem: '8GB', cores: 4, price: 80},
            {mem: '16GB', cores: 8, price: 160},
            {mem: '32GB', cores: 12, price: 320},
            {mem: '48GB', cores: 16, price: 480},
            {mem: '64GB', cores: 20, price: 640},
            {mem: '96GB', cores: 24, price: 960},
        ];

        $scope.storageList = [
            {size: '10GB', price: 5},
            {size: '20GB', price: 10},
            {size: '30GB', price: 15},
            {size: '40GB', price: 20},
            {size: '50GB', price: 25},
            {size: '60GB', price: 30},
            {size: '70GB', price: 35},
            {size: '80GB', price: 40},
            {size: '90GB', price: 45},
            {size: '100GB', price: 50},
        ];

        $scope.totalPrice = 0;

        $scope.$watch('cpuMem + storage', function() {
            $scope.totalPrice = $scope.cpuMemList[$scope.cpuMem].price + $scope.storageList[$scope.storage].price;
        });
    }]);
