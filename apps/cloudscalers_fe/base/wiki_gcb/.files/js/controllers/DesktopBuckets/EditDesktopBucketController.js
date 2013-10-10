cloudscalersControllers
    .controller('EditDesktopBucketController', ['$scope', '$routeParams', 'DesktopBucketService', function($scope, $routeParams, DesktopBucketService) {
        $scope.bucket = DesktopBucketService.getById(parseFloat(location.hash.substr(2)));

        $scope.bucket.isValid = function() {
            return this.projectName && this.users.length > 0 && this.storage;
        };

        $scope.bucket.addNewUser = function() {
            this.users.push(this.newUser);
            this.newUser = { email: '', userType: '' };
        };

        $scope.update = function() {
            DesktopBucketService.save($scope.bucket);
            location.href = "My Desktop Buckets"
        };
    }])
