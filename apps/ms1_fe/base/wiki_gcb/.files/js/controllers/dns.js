(function() {
  'use strict';
  //jshint latedef: nofunc
  angular
    .module('cloudscalers.controllers')
    .controller('DNSController', DNSController);

  function DNSController($scope, DNSService, Buckets, LoadingDialog) {
    $scope.domains = DNSService.getAll();
    $scope.buckets = Buckets.getAll();

    $scope.resetNewDomain = resetNewDomain;
    $scope.isRecordValid = isRecordValid;
    $scope.addRecord = addRecord;
    $scope.addDomain = addDomain;
    $scope.removeDomain = removeDomain;
    $scope.removeRecord = removeRecord;

    $scope.resetNewDomain();

    function resetNewDomain() {
      $scope.newDomain = {
        id: Math.random() * 1000000000,
        name: '',
        bucket: null,
        records: [
          {type: 'CNAME', name: 'www.mysite.com', hostname: '', ipAddress: ''},
          {type: 'NS', name: '', hostname: 'ns1.cloudscalers.com', ipAddress: ''},
          {type: 'NS', name: '', hostname: 'ns2.cloudscalers.com', ipAddress: ''}
        ],
        newRecord: {}
      };

      $scope.newDomain.isValid = function() {
        return $scope.newDomain.name && $scope.newDomain.bucket;
      };
    }

    function isRecordValid(record) {
      return record.type;
    }

    function addRecord(domain) {
      domain.records.push(domain.newRecord);
      domain.newRecord = {};
      DNSService.save(domain);
      LoadingDialog.show('Adding DNS record');
    }

    function addDomain() {
      $scope.domains.push($scope.newDomain);
      DNSService.add($scope.newDomain);
      $scope.resetNewDomain();
      LoadingDialog.show('Creating domain');
    }

    function removeDomain(domainIndex) {
      $scope.domains.splice(domainIndex, 1);
      DNSService.saveAll($scope.domains);
      LoadingDialog.show('Removing domain');
    }

    function removeRecord(domain, recordIndex) {
      domain.records.splice(recordIndex, 1);
      DNSService.saveAll($scope.domains);
      LoadingDialog.show('Removing DNS record');
    }
  }
})();
