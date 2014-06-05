angular.module('cloudscalers.controllers')
    .controller('PricingAllController', ['$scope', function($scope) {
        $scope.pricingModel = 'mo';
        $scope.os = 'Linux';

        $scope.plans = {
            'Linux': {
                mo: [
                    {mem: '512MB', cores: 1, primary: 10, recommended: false, price: 5   },
                    {mem: '1GB',   cores: 1, primary: 10, recommended: false, price: 10  },
                    {mem: '2GB',   cores: 2, primary: 10, recommended: false, price: 20  },
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 36  },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 64  },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 112 }
                ],
                hr: [
                    {mem: '512MB', cores: 1, primary: 10, recommended: false, price: 0.0069 },
                    {mem: '1GB',   cores: 1, primary: 10, recommended: false, price: 0.0139 },
                    {mem: '2GB',   cores: 2, primary: 10, recommended: false, price: 0.0278 },
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 0.0500 },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 0.0889 },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 0.1556 }
                ]
            },
            'Windows Standard': {
                mo: [
                    {mem: '2GB',   cores: 2, primary: 10, recommended: false, price: 33  },
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 62  },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 116 },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 217 }
                ],
                hr: [
                    {mem: '2GB',   cores: 2, primary: 10, recommended: false, price: 0.0458 },
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 0.0861 },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 0.1611 },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 0.3014 }
                ]
            },
            'Windows Essentials': {
                mo: [
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 72  },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 128 },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 224 }
                ],
                hr: [
                    {mem: '4GB',   cores: 2, primary: 10, recommended: true,  price: 0.1    },
                    {mem: '8GB',   cores: 4, primary: 10, recommended: false, price: 0.1778 },
                    {mem: '16GB',  cores: 8, primary: 10, recommended: false, price: 0.3111 }
                ]
            },
        };
    }]);
