myAppControllers
    .controller('DNSController', ['$scope', 'DNSService', 'Buckets', function($scope, DNSService, Buckets) {
        $scope.domains = DNSService.getAll();
        $scope.buckets = Buckets.getAll();
        
        $scope.resetNewDomain = function() {
            $scope.newDomain = {
                id: Math.random() * 1000000000,
                name: '',
                bucket: null, 
                records: [
                    {type: 'CNAME', name: 'www.mysite.com', hostname: '', ipAddress: ''},
                    {type: 'NS', name: '', hostname: 'ns1.cloudscalers.com', ipAddress: ''},
                    {type: 'NS', name: '', hostname: 'ns2.cloudscalers.com', ipAddress: ''},
                ], newRecord: {}};

            $scope.newDomain.isValid = function() {
                return $scope.newDomain.name && $scope.newDomain.bucket;
            };
        };

        $scope.resetNewDomain();

        $scope.isRecordValid = function(record) {
            return record.type;
        };

        $scope.addRecord = function(domain, record) {
            domain.records.push(domain.newRecord);
            domain.newRecord = {};
            DNSService.save(domain);
            showLoading('Adding DNS record');
        }

        $scope.addDomain = function() {
            $scope.domains.push($scope.newDomain);
            DNSService.add($scope.newDomain);
            $scope.resetNewDomain();
            showLoading('Creating domain');
        };

        $scope.removeDomain = function(domainIndex) {
            $scope.domains.splice(domainIndex, 1);
            DNSService.saveAll($scope.domains);
            showLoading('Removing domain');
        };

        $scope.removeRecord = function(domain, recordIndex) {
            domain.records.splice(recordIndex, 1);
            DNSService.saveAll($scope.domains);
            showLoading('Removing DNS record');
        };


    }])
