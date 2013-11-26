describe("CloudSpaceNavigatorController", function(){
    var $scope, navigatorCtrl, sessionCtrl, $q, $httpBackend, CloudSpace, Account, cloudListDefer, accountListDefer;
    beforeEach(module('cloudscalers'));

    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
        $httpBackend = _$httpBackend_;
        $controller = _$controller_;
        defineUnitApiStub($httpBackend);
        
        $scope = $rootScope.$new();
        $q = _$q_;

        cloudListDefer = $q.defer();
        accountListDefer = $q.defer();

        CloudSpace = {
            current : jasmine.createSpy('current'), 
            setCurrent : jasmine.createSpy('setCurrent'), 
            list: jasmine.createSpy('list').andReturn(cloudListDefer.promise)
        };

        Account = {
            list: jasmine.createSpy('list').andReturn(accountListDefer.promise)
        };
        
        sessionCtrl = $controller('AuthenticatedSessionController', {
            $scope: $scope,
            CloudSpace: CloudSpace,
            Account: Account
        });
        navigatorCtrl = $controller('CloudSpaceNavigatorController', {$scope : $scope});
        cloudListDefer.resolve([
                               {cloudSpaceId: 2, accountId: 1},
                               {cloudSpaceId: 3, accountId: 2},
                               ]);
        accountListDefer.resolve([
                                 {id: 1, name: 'Account 1'},
                                 {id: 2, name: 'Account 2'}
                                 ]);
    }));

    it('builds accounts & cloudspaces hierarchy from lists of cloudspaces & accounts', function() {
        expect($scope.AccountCloudSpaceHierarchy).toBeUndefined();
        $scope.$digest();
        expect($scope.AccountCloudSpaceHierarchy).toEqual([
            {id: 1, name: 'Account 1', cloudspaces: [{cloudSpaceId: 2, accountId: 1}]},
            {id: 2, name: 'Account 2', cloudspaces: [{cloudSpaceId: 3, accountId: 2}]}
        ]);
    });



});