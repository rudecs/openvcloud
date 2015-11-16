// angular.module('cloudscalers.controllers')
//     .controller('StorageController', ['$scope', '$modal', 'Storage','$ErrorResponseAlert',
//         function ($scope, $modal, Storage, $ErrorResponseAlert) {
//           $scope.$watch('currentSpace', function() {
//             if($scope.currentSpace){
//               Storage.listShares($scope.currentSpace.id).then(
//                 function(data) {
//                   $scope.shares = data;
//                   console.log($scope.shares);
//                   // $scope.sharesLoader = false;
//                 },
//                 function(reason) {
//                   $ErrorResponseAlert(reason);
//                   // $scope.sharesLoader = false;
//                 }
//               );
//             }
//           });
//         }
//     ]);
