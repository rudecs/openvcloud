describe("AccountAccessManagementController tests", function(){
    var $scope, ctrl, $q, $window = {}, $httpBackend, Account, getAccountDefer, addUserDefer;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
    	$httpBackend = _$httpBackend_;
        $controller = _$controller_;
		defineUnitApiStub($httpBackend);
		
        $q = _$q_;
        getAccountDefer = $q.defer();
        addUserDefer = $q.defer();
        Account = {
            get: jasmine.createSpy('get').andReturn(getAccountDefer.promise),
            addUser: jasmine.createSpy('addUser').andReturn(addUserDefer.promise),
        };

        $scope = $rootScope.$new();
        $scope.currentSpace = {
            cloudSpaceId: 15,
            accountId: 1
        };
        $scope.currentAccount = {};
        ctrl = $controller('AccountAccessManagementController', {
            $scope: $scope,
            Account: Account
        });

        getAccountDefer.resolve({
            name: 'Linny Miller',
            descr: 'Mr. Linny Miller',
            acl: [{
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "linny"
                }, {
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "harvey"
                }
            ]
        });
        $scope.$digest();
    }));

});

