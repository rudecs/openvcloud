'use strict';

/* Controllers */

angular.module('myApp.controllers', ['ui.bootstrap'])

    .controller('BucketListCtrl', ['$scope', 'Buckets', function($scope, Buckets) {
        $scope.buckets = Buckets.getAll();
    }])

    .controller('BucketNewCtrl', ['$scope', 'Buckets', '$location', function($scope, Buckets) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            name: '',
            plan: '',
            region: '',
            status: 'active',
            image: ''
        };
  
        $scope.bucketValid = function() {
            return $scope.bucket.name && $scope.bucket.plan && $scope.bucket.region && $scope.bucket.image;
        };

        $scope.saveBucket = function() {
            Buckets.add($scope.bucket);
            location.href = "#/list";
        };
    }]);