angular.module('cloudscalers.controllers')
    .controller('EditDesktopBucketController', ['$scope', '$routeParams', 'DesktopBucketService', function($scope, $routeParams, DesktopBucketService) {
        if (DesktopBucketService.getAll() && DesktopBucketService.getAll().length == 1)
            $scope.bucket = DesktopBucketService.getAll()[0];
        else
            $scope.bucket = {
                id: Math.random() * 1000000000,
                projectName: '',
                users: [],
                newUser: { email: '', userType: '' },
                storage: 100,
                locations: [false, false, false],
                numOfficeLicenses: 5,
                numFullOfficeLicenses: 0,
            };

        $scope.bucket.isValid = function() {
            return this.projectName && this.storage && _.any(this.locations);
        };

        $scope.bucket.addNewUser = function() {
            this.users.push(this.newUser);
            this.newUser = { email: '', userType: '' };
            DesktopBucketService.save($scope.bucket);
        };

        $scope.update = function() {
            DesktopBucketService.save($scope.bucket);
            location.href = "My Desktop Buckets";
        };
    }])
