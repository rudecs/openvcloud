angular.module('cloudscalers.controllers')
    .controller('PricingAllController', ['$scope', function($scope) {
        $scope.pricingModel = 'mo';
        $scope.os = 'linux';
        $scope.activePlansCount = 6;

        $scope.plans = [
            {name: 'Mothership 1', mem: '512MB', cores: 1, primary: 10, recommended: false, 
                linux:   {mo: 5,   hr: 0.0083},
                windows: {mo: '-',  hr: '-'},
                windows_essentials: { mo: '-', hr: '-'}
            },
            {name: 'Mothership 2', mem: '1GB',   cores: 1, primary: 10, recommended: false,
                linux:   {mo: 10,  hr: 0.0153},
                windows: {mo: '-',  hr: '-'},
                windows_essentials: { mo: '-', hr: '-'}
            },
            {name: 'Mothership 3', mem: '2GB',   cores: 2, primary: 10, recommended: false, 
                linux:   {mo: 20,  hr: 0.0278},
                windows: {mo: 33,  hr: 0.0556},
                windows_essentials: { mo: '-', hr: '-'}
            },
            {name: 'Mothership 4', mem: '4GB',   cores: 2, primary: 10, recommended: true, 
                linux:   {mo: 36,  hr: 0.0500},
                windows: {mo: 62,  hr: 0.1000},
                windows_essentials: { mo: 72, hr: 0.1}
            },
            {name: 'Mothership 5', mem: '8GB',   cores: 4, primary: 10, recommended: false, 
                linux:   {mo: 64,  hr: 0.0889},
                windows: {mo: 116, hr: 0.1778},
                windows_essentials: { mo: 128, hr: 0.1778}
            },
            {name: 'Mothership 6', mem: '16GB',  cores: 8, primary: 10, recommended: false, 
                linux:   {mo: 112, hr: 0.1556},
                windows: {mo: 217, hr: 0.3111} ,
                windows_essentials: { mo: 224, hr: 0.3111}
            }
        ];

        $scope.$watch('pricingModel + os', function() {
            $scope.activePlansCount = _.countBy($scope.plans, function(plan) { return plan[$scope.os][$scope.pricingModel] != '-'; })[true];
        }, true);
    }]);