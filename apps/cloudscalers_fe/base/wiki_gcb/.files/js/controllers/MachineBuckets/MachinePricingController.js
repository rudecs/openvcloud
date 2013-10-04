cloudscalersControllers
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.cpuMem = 0;
        $scope.storage = 0;
        $scope.archive = 0;
        $scope.location = 0;

        $scope.cpuMemList = [
            {mem: '512MB', cores: 1, price: 2.5, primary: 10},
            {mem: '1GB', cores: 1, price: 8.5, primary: 20},
            {mem: '2GB', cores: 2, price: 17, primary: 20},
            {mem: '4GB', cores: 2, price: 34, primary: 20},
            {mem: '8GB', cores: 4, price: 71, primary: 20},
            {mem: '16GB', cores: 8, price: 139, primary: 20},
            {mem: '32GB', cores: 12, price: 275, primary: 20},
            {mem: '48GB', cores: 16, price: 411, primary: 20},
            {mem: '64GB', cores: 20, price: 547, primary: 20},
            {mem: '96GB', cores: 24, price: 819, primary: 20},
        ];

        $scope.storageList = [
            {size: '0GB', price: 0},
            {size: '10GB', price: 1.5},
            {size: '20GB', price: 3},
            {size: '30GB', price: 4.5},
            {size: '40GB', price: 6},
            {size: '50GB', price: 7.5},
            {size: '100GB', price: 15},
            {size: '250GB', price: 37.5},
            {size: '500GB', price: 75},
            {size: '1TB', price: 150},
        ];

        $scope.archiveList = [
            {size: '0GB', price: 0},
            {size: '10GB', price: 0.76},
            {size: '20GB', price: 1.52},
            {size: '30GB', price: 2.28},
            {size: '40GB', price: 3.04},
            {size: '50GB', price: 3.80},
            {size: '100GB', price: 7.60},
            {size: '250GB', price: 19.00},
            {size: '500GB', price: 38.00},
            {size: '1TB', price: 76.00},
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
