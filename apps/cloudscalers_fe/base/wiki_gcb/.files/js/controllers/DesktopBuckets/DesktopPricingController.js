cloudscalersControllers
    .controller('DesktopPricingController', ['$scope', '$timeout', function($scope, $timeout) {
        $scope.numOfUsers = 1;
        $scope.totalPrice = 10;

        $scope.numOfTB = 1;
        $scope.totalPriceOfStorage = 0.86;

        $scope.$watch('numOfUsers + numOfTB', function() {
            $scope.totalPrice = $scope.numOfUsers * 10;
            $scope.totalPriceOfStorage = $scope.numOfTB * 0.76; 
            $scope.totalPriceOfStorage = Math.round($scope.totalPriceOfStorage * 100) / 100
        });

        $timeout(function() {

            $( "#numOfUsers" ).spinner({
                min: 1,
                step: 1,
                stop: function() { 
                    $scope.numOfUsers = parseInt($( "#numOfUsers" ).val());
                    $scope.$digest();
                }
            });
            

            $( "#numOfTB" ).spinner({
                min: 1,
                step: 1,
                stop: function() { 
                    $scope.numOfTB = parseInt($( "#numOfTB" ).val());
                    $scope.$digest();
                }
            });

        }, 0);
    }]);
