cloudscalersControllers
    .controller('PricingController', ['$scope', function($scope) {
        $scope.cpu = 0;
        $scope.memory = 0;
        $scope.storage = 0;
        $scope.location = 0;

        $scope.cpuList = [
            {cores: 1, price: 5},
            {cores: 1, price: 10},
            {cores: 2, price: 20},
            {cores: 2, price: 40},
            {cores: 4, price: 80},
            {cores: 8, price: 160},
            {cores: 12, price: 320},
            {cores: 16, price: 480},
            {cores: 20, price: 640},
            {cores: 24, price: 960},
        ];

        $scope.memoryList = [
            {memory: '512MB', price: 5},
            {memory: '1GB', price: 10},
            {memory: '2GB', price: 20},
            {memory: '4GB', price: 40},
            {memory: '8GB', price: 80},
            {memory: '16GB', price: 160},
            {memory: '32GB', price: 320},
            {memory: '48GB', price: 480},
            {memory: '64GB', price: 640},
            {memory: '96GB', price: 960},
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

        $scope.locationsList = [
            {number: 1, price: 5},
            {number: 2, price: 10},
        ];

        $scope.totalPrice = 0;

        $scope.$watch('cpu + memory + storage + location', function() {
            $scope.totalPrice = 
                $scope.locationsList[$scope.location].price * (
                    $scope.cpuList[$scope.cpu].price + $scope.memoryList[$scope.memory].price + $scope.storageList[$scope.storage].price);
        });
    }]);
