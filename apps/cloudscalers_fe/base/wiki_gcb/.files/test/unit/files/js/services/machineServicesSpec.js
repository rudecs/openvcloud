describe('Cloudscalers machine services', function() {


	beforeEach(module('machineServices'));
	
	describe('User service', function(){
		var $httpBackend, User;
		beforeEach(inject(function(_$httpBackend_) {
			$httpBackend = _$httpBackend_;
			
			inject(function($injector) {
			    User = $injector.get('User');
			  });
		
		}));
		
		it('Login succeeds',function(){			
			defineUnitApiStub($httpBackend);

			var loginResult = User.login('testuser','testpass');

			expect(loginResult).toBeDefined();
			expect(loginResult.authKey).toBeUndefined();
			expect(loginResult.username).toBe('testuser');
			
			$httpBackend.flush();
			
			expect(loginResult.username).toBe('testuser');
			expect(loginResult.authKey).toBe('yep123456789');
			expect(loginResult.error).toBeUndefined();
		});
		
		it('Login fails',function(){
			defineUnitApiStub($httpBackend);
						
			var loginResult = User.login('error','testpass');

			expect(loginResult).toBeDefined();
			expect(loginResult.error).toBeUndefined();
			expect(loginResult.username).toBe('error');
			
			$httpBackend.flush();
			
			expect(loginResult.username).toBe('error');
			expect(loginResult.authKey).toBeUndefined();
			expect(loginResult.error).toBe(403);
		});
		
		
	});

	describe('Machine Service', function(){
		var $httpBackend, Machine;

		beforeEach(inject(function(_$httpBackend_) {
			$httpBackend = _$httpBackend_;
			
			inject(function($injector) {
			    Machine = $injector.get('Machine');
			  });
		}))

			it('test machine list', function(){
				defineUnitApiStub($httpBackend);
				                
				machineListResult = Machine.list(0);
				$httpBackend.flush();

				expect(machineListResult).toBeDefined();
				expect(machineListResult.error).toBeUndefined();
				expect(machineListResult.length).toBe(2);
				expect(machineListResult[0].imageId).toBe(0);
				expect(machineListResult[0].name).toBe("test");
				expect(machineListResult[0].id).toBe(0);
			});

			it('test machine get', function(){
				defineUnitApiStub($httpBackend);
				machineGetResult = Machine.get(0);
				expect(machineGetResult.id).toBe(0);
				
				$httpBackend.flush();

				expect(machineGetResult).toBeDefined();
				expect(machineGetResult.error).toBeUndefined();
				expect(machineGetResult.name).toBe("test");
				expect(machineGetResult.id).toBe(0);

			});

			it('test machine get failure', function(){
				defineUnitApiStub($httpBackend);
				machineGetErrorResult = Machine.get(44534);
				$httpBackend.flush();

				expect(machineGetErrorResult).toBeDefined();
				expect(machineGetErrorResult.error).toBe(500);
			});

                        it('test machine create', function(){
				defineUnitApiStub($httpBackend);
				var machineCreateResult = Machine.create(0, 'test_create', 'Test Description', 0, 0);
                                //expect(machineCreateResult.id).toBeUndefined();
				
				$httpBackend.flush();

				expect(machineCreateResult).toBeDefined();
				expect(machineCreateResult.error).toBeUndefined();
				expect(machineCreateResult.id).toBe(3);
			});

			
		
		});

        describe('Sizes Service', function(){
		var $httpBackend, Sizes;

		beforeEach(inject(function(_$httpBackend_) {
			$httpBackend = _$httpBackend_;
			
			inject(function($injector) {
			    Size = $injector.get('Size');
			  });
		}))

			it('test size list', function(){
				defineUnitApiStub($httpBackend);
				                
				sizeListResult = Size.list();
				$httpBackend.flush();

				expect(sizeListResult).toBeDefined();
				expect(sizeListResult.error).toBeUndefined();
				expect(sizeListResult.length).toBe(3);
				expect(sizeListResult[0].id).toBe(0);
				expect(sizeListResult[0].name).toBe("small");
				expect(sizeListResult[1].CU).toBe(2);
			});

		
		});



	});
	
	

