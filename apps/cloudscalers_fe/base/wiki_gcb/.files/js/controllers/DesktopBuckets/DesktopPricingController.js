cloudscalersControllers
    .controller('DesktopPricingController', ['$scope', '$timeout', function($scope, $timeout) {
        $scope.numOfUsers = 1;
        $scope.totalPrice = 10;

        $scope.$watch('numOfUsers', function() {
            $scope.totalPrice = $scope.numOfUsers * 10;
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
        }, 0);
    }]);
