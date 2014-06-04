describe("CloudSpaceAccessManagementController tests", function(){
    var $scope, ctrl, $q, $window = {}, $httpBackend, CloudSpace, getCloudSpaceDefer, addUserDefer;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
    	$httpBackend = _$httpBackend_;
        $controller = _$controller_;
		defineUnitApiStub($httpBackend);
		
        $q = _$q_;
        getCloudSpaceDefer = $q.defer();
        addUserDefer = $q.defer();
        CloudSpace = {
            get: jasmine.createSpy('get').andReturn(getCloudSpaceDefer.promise),
            addUser: jasmine.createSpy('addUser').andReturn(addUserDefer.promise)
        };

        $scope = $rootScope.$new();
        $scope.currentSpace = {
            cloudSpaceId: 15
        };
        ctrl = $controller('CloudSpaceAccessManagementController', {
            $scope: $scope,
            CloudSpace: CloudSpace
        });

        getCloudSpaceDefer.resolve({
            name: 'Development',
            descr: 'Development machine',
            acl: [{
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "user 1"
                }, {
                    "type": "U",
                    "guid": "",
                    "right": "CXDRAU",
                    "userGroupId": "user 2"
                }
            ]
        });
        $scope.$digest();
    }));


    it('addUser adds a new user to the list of users', function() {
        $scope.newUser.nameOrEmail = 'User 4';
        $scope.addUser();
        addUserDefer.resolve("Success");
        $scope.$digest();
        
        expect(CloudSpace.addUser).toHaveBeenCalled();
        expect($scope.userError).toEqual(false);
    });

});

