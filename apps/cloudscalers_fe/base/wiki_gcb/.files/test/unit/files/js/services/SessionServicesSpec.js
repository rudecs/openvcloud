describe('Cloudscalers SessionServices', function() {
	beforeEach(module('cloudscalers.services'));
	
	describe('User service', function(){
		var $httpBackend, User, SessionData;
		beforeEach(inject(function(_$httpBackend_, _User_, _SessionData_) {
			$httpBackend = _$httpBackend_;
			User = _User_;
            SessionData = _SessionData_;
            SessionData.setUser(null);
            defineUnitApiStub($httpBackend);
		}));
		
		it('handles successful login',function(){			
			var loginResult = {};
			User.login().then(function(result){loginResult.key = result;},function(reason){});
			$httpBackend.flush();
			
            expect(SessionData.getUser().api_key).toBe('yep123456789');
		});
		
		it('handles failed login',function(){

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
        	SessionData.setUser({username:'123'});

            User.logout();
            expect(SessionData.getUser()).toBeUndefined();
        });
	});
});