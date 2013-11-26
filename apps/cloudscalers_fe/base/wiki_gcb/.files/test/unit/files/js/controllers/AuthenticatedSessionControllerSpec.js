describe("AuthenticatedSessionController tests", function(){
    var $scope, ctrl, User, $q, $window = {}, $httpBackend, CloudSpace, Account, cloudListDefer, accountListDefer;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
    	$httpBackend = _$httpBackend_;
        $controller = _$controller_;
		defineUnitApiStub($httpBackend);
		
        $scope = $rootScope.$new();
        User = {logout : jasmine.createSpy('logout'), current: function() {}};
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
    }));


    it('logout', function() {
    	$window.location = "http://test.com/mylocation#/blablabla";

    	inject(function($controller){
    		ctrl = $controller('AuthenticatedSessionController', {$scope : $scope, User : User, $window: $window});
    	});
        
        $scope.logout();

        expect(User.logout).toHaveBeenCalled();
        expect($window.location).toBe("http://test.com/");
    });

    describe('if the current space is not set', function() {
        beforeEach(function() {
            CloudSpace.current.andReturn(undefined);

            ctrl = $controller('AuthenticatedSessionController', {
                $scope : $scope, 
                CloudSpace: CloudSpace,
                Account: Account});

            cloudListDefer.resolve([
                                   {cloudSpaceId: 2, accountId: 1},
                                   {cloudSpaceId: 3, accountId: 2},
                                   ]);
            accountListDefer.resolve([
                                     {id: 1, name: 'Account 1'},
                                     {id: 2, name: 'Account 2'}
                                     ]);
            $scope.$digest();
        });

        it('loads cloudspaces & accounts', function() {
            expect($scope.cloudspaces).toBeDefined();
            expect($scope.accounts).toBeDefined();
        })

        it('sets the first cloudspace as current cloudspace', function() {
            expect(CloudSpace.current).toHaveBeenCalled();
            expect(CloudSpace.list).toHaveBeenCalled();
            
            expect($scope.currentSpace).toBeDefined();
            expect($scope.currentSpace.cloudSpaceId).toEqual(2);
        });

        it('account is updated when the current space is selected', function() {
            $scope.setCurrentCloudspace($scope.cloudspaces[1]);
            
            expect($scope.currentSpace).toEqual($scope.cloudspaces[1]);
            expect($scope.currentAccount).toBeDefined();
            expect($scope.currentAccount.id).toEqual(2);
        });
    });
});

