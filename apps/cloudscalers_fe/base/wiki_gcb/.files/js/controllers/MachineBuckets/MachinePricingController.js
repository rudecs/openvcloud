cloudscalersControllers
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.cpuMem = 0;
        $scope.storage = 0;
        $scope.archive = 0;
        $scope.location = 0;

        $scope.cpuMemList = [
            {mem: '512MB', cores: 1, price: 7.5, primary: 10},
            {mem: '1GB', cores: 1, price: 15, primary: 10},
            {mem: '2GB', cores: 2, price: 18, primary: 10},
            {mem: '4GB', cores: 2, price: 36, primary: 10},
            {mem: '8GB', cores: 4, price: 70, primary: 10},
            {mem: '16GB', cores: 8, price: 140, primary: 10},
            {mem: '32GB', cores: 12, price: 250, primary: 10},
            {mem: '48GB', cores: 16, price: 350, primary: 10},
            {mem: '64GB', cores: 20, price: 465, primary: 10},
            {mem: '96GB', cores: 24, price: 700, primary: 10},
        ];

        $scope.storageList = [
            {size: '10GB', price: 0},
            {size: '20GB', price: 2.5},
            {size: '30GB', price: 5},
            {size: '40GB', price: 7.5},
            {size: '50GB', price: 10},
            {size: '100GB', price: 22.5},
            {size: '250GB', price: 60},
            {size: '500GB', price: 122.5},
            {size: '1TB', price: 247.5},
        ];

        $scope.archiveList = [
            {size: '0GB', price: 0},
            {size: '10GB', price: 0.86},
            {size: '20GB', price: 1.71},
            {size: '30GB', price: 2.57},
            {size: '40GB', price: 3.42},
            {size: '50GB', price: 4.28},
            {size: '100GB', price: 8.55},
            {size: '250GB', price: 21.38},
            {size: '500GB', price: 42.75},
            {size: '1TB', price: 85.50},
        ];

        $scope.locationsList = [
            {number: 0, price: 0},
            {number: 1, price: 1},
            {number: 2, price: 2},
        ];

        $scope.totalPrice = 0;

        $scope.$watch('cpuMem + storage + archive + location', function() {
            // Below I added 2.5 USD because the base package has 10GB which costs 2.5 USD
            $scope.totalPrice = (($scope.locationsList[$scope.location].price + 1) * ($scope.storageList[$scope.storage].price + 2.5)) + $scope.cpuMemList[$scope.cpuMem].price + $scope.archiveList[$scope.archive].price;
            $scope.totalPrice = Math.round($scope.totalPrice * 100) / 100
        });
    }]);
