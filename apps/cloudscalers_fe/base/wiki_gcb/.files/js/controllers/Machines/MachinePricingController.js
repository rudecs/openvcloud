angular.module('cloudscalers.controllers')
    .controller('MachinePricingController', ['$scope', function($scope) {
        $scope.pricingModel = 'mo';
        $scope.os = 'linux';

        $scope.plans = [
            {name: 'Mothership 1', mem: '512MB', cores: 1, primary: 10, recommended: false, 
                linux:   {mo: 6,   hr: 0.0083},
                windows: {mo: 12,  hr: 0.0167} 
            },
            {name: 'Mothership 2', mem: '1GB',   cores: 1, primary: 10, recommended: true,
                linux:   {mo: 11,  hr: 0.0153},
                windows: {mo: 22,  hr: 0.0306} 
            },
            {name: 'Mothership 3', mem: '2GB',   cores: 2, primary: 10, recommended: false, 
                linux:   {mo: 20,  hr: 0.0278},
                windows: {mo: 40,  hr: 0.0556} 
            },
            {name: 'Mothership 4', mem: '4GB',   cores: 2, primary: 10, recommended: false, 
                linux:   {mo: 36,  hr: 0.0500},
                windows: {mo: 72,  hr: 0.1000} 
            },
            {name: 'Mothership 5', mem: '8GB',   cores: 4, primary: 10, recommended: false, 
                linux:   {mo: 64,  hr: 0.0889},
                windows: {mo: 128, hr: 0.1778} 
            },
            {name: 'Mothership 6', mem: '16GB',  cores: 8, primary: 10, recommended: false, 
                linux:   {mo: 112, hr: 0.1556},
                windows: {mo: 224, hr: 0.3111} 
            }
        ];
    }]);
