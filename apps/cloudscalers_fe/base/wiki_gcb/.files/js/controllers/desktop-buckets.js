cloudscalersControllers
    .controller('CreateDesktopBucketController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.bucket = {
            id: Math.random() * 1000000000,
            projectName: '',
            users: [],
            newUser: { email: '', userType: '' },
            storage: 100,
            locations: [false, false, false],
            numOfficeLicenses: 5,
            numFullOfficeLicenses: 0,

            addNewUser: function() {
                this.users.push(this.newUser);
                this.newUser = { email: '', userType: '' };
            },

            isValid: function() {
                return this.projectName && this.users.length > 0 && this.storage;
            }
        };

        $scope.create = function() {
            DesktopBucketService.add($scope.bucket);
            location.href = "My Desktop Buckets";
        };
    }])

    .controller('ListDesktopBucketsController', ['$scope', 'DesktopBucketService', function($scope, DesktopBucketService) {
        $scope.buckets = DesktopBucketService.getAll();
        $scope.numOfDataLocations = function(bucket) {
            if (!bucket.locations || !bucket.locations.length)
                return 0;
            var numOfLocations = 0;
            for (var i = 0; i < bucket.locations.length; i++) {
                if (bucket.locations[i]) {
                    numOfLocations++;
                }
            }
            return numOfLocations;
        }
    }])

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
