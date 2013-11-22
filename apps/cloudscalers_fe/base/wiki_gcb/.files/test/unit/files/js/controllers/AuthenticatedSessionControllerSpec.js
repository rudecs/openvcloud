describe("AuthenticatedSessionController tests", function(){
    var $scope, ctrl, $controller, User, $q, $window = {}, $httpBackend;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_, _$q_, _$httpBackend_) {
    	$httpBackend = _$httpBackend_;
		defineUnitApiStub($httpBackend);
		
        $scope = $rootScope.$new();
        User = {logout : jasmine.createSpy('logout')};
        //$controller = _$controller_;
        $q = _$q_;
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
});

