describe('Cloudscalers SessionServices', function() {
	beforeEach(module('cloudscalers.SessionServices'));
	
	describe('User service', function(){
		var $httpBackend, User;
		beforeEach(inject(function(_$httpBackend_, _User_, _APIKey_) {
			$httpBackend = _$httpBackend_;
			User = _User_;
            APIKey = _APIKey_;
            APIKey.clear();
            defineUnitApiStub($httpBackend);
		}));
		
		it('handles successful login',function(){			
            expect(APIKey.get()).toBeNull();

			var loginResult = User.login();
			$httpBackend.flush();
			
            expect(loginResult).toBeDefined();
            expect(loginResult.api_key).toBe('yep123456789');
            expect(APIKey.get()).toBe('yep123456789');
			expect(loginResult.error).toBeFalsy();
		});
		
		it('handles failed login',function(){
            expect(APIKey.get()).toBeNull();

			var loginResult = User.login('error','testpass');

			$httpBackend.flush();
			
			expect(loginResult.api_key).toBeUndefined();
			expect(loginResult.error).toBe(403);
		});

        it('can logout', function() {
            APIKey.set('123');

            User.logout();
            expect(APIKey.get()).toBeNull();
        });
	});
});