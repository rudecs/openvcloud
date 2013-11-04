cloudscalersControllers
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.cpuMem = 0;
        $scope.storage = 0;
        $scope.archive = 0;
        $scope.location = 0;

        $scope.cpuMemList = [
            {mem: '512MB', cores: 1, price: 5, primary: 10},
            {mem: '1GB', cores: 1, price: 8, primary: 10},
            {mem: '2GB', cores: 2, price: 17, primary: 10},
            {mem: '4GB', cores: 2, price: 35, primary: 10},
            {mem: '8GB', cores: 4, price: 73, primary: 10},
            {mem: '16GB', cores: 8, price: 145, primary: 10},
            {mem: '32GB', cores: 12, price: 289, primary: 10},
            {mem: '48GB', cores: 16, price: 433, primary: 10},
            {mem: '64GB', cores: 20, price: 577, primary: 10},
            {mem: '96GB', cores: 24, price: 865, primary: 10},
        ];

        $scope.storageList = [
            {size: '0GB', price: 0},
            {size: '10GB', price: 1},
            {size: '20GB', price: 2},
            {size: '30GB', price: 3},
            {size: '40GB', price: 4},
            {size: '50GB', price: 5},
            {size: '100GB', price: 10},
            {size: '250GB', price: 25},
            {size: '500GB', price: 50},
            {size: '1TB', price: 100},
        ];

        $scope.archiveList = [
            {size: '0GB', price: 0},
            {size: '10GB', price: 0.95},
            {size: '20GB', price: 1.90},
            {size: '30GB', price: 2.85},
            {size: '40GB', price: 3.80},
            {size: '50GB', price: 4.75},
            {size: '100GB', price: 9.50},
            {size: '250GB', price: 23.75},
            {size: '500GB', price: 47.50},
            {size: '1TB', price: 95.00},
        ];

        $scope.locationsList = [
            {number: 0, price: 0},
            {number: 1, price: 1},
            {number: 2, price: 2},
        ];

        $scope.totalPrice = 0;

        $scope.$watch('cpuMem + storage + archive + location', function() {
            $scope.totalPrice = ($scope.locationsList[$scope.location].price * $scope.storageList[$scope.storage].price) + $scope.cpuMemList[$scope.cpuMem].price + $scope.archiveList[$scope.archive].price;
            $scope.totalPrice = Math.round($scope.totalPrice * 100) / 100
        });
    }]);
