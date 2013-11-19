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

			var loginResult = {};
			User.login().then(function(result){loginResult.key = result;},function(reason){});
			$httpBackend.flush();
			
            expect(loginResult.key).toBe('yep123456789');
            expect(APIKey.get()).toBe('yep123456789');
		});
		
		it('handles failed login',function(){
            expect(APIKey.get()).toBeNull();

			var loginResult = {};
			User.login('error','testpass').
			then(
					function(result){},
					function(reason){
						loginResult.reason = reason.status;
			});

			$httpBackend.flush();
			
			expect(loginResult.reason).toBe(403);
		});

        it('can logout', function() {
            APIKey.set('123');

            User.logout();
            expect(APIKey.get()).toBeNull();
        });
	});
});