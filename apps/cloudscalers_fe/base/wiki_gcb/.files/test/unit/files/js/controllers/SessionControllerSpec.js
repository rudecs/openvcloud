describe("SessionController tests", function(){
    var scope, ctrl, $controller, User = 123;
    
    beforeEach(module('cloudscalers'));
    
    beforeEach(inject(function($rootScope, _$controller_) {
        scope = $rootScope.$new();
        User = {login : jasmine.createSpy('login')};
        $controller = _$controller_;
    }));

    it("handles failure", function() {
        User.login.andReturn({error: 403});
        ctrl = $controller('SessionController', {$scope : scope, User : User});

        scope.username = 'error';
        scope.password = 'pa$$w0rd';
        scope.login();

        expect(User.login).toHaveBeenCalledWith('error', 'pa$$w0rd');
        expect(scope.loginResult.error).toBe(403);
    });

    it('handles success', function() {
        User.login.andReturn({});
        ctrl = $controller('SessionController', {$scope : scope, User : User});

        scope.username = 'user1';
        scope.password = 'pa$$w0rd';
        scope.login();

        expect(User.login).toHaveBeenCalledWith('user1', 'pa$$w0rd');
        expect(scope.loginResult.error).toBeUndefined();
    });
});

