describe('Cloudscalers machine services', function() {
	beforeEach(module('cloudscalers.machineServices'));
	
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

	describe('Machine Service', function(){
		var $httpBackend, $sce, Machine, APIKey;

		beforeEach(inject(function(_$httpBackend_, _$sce_, _Machine_, _APIKey_) {
			$httpBackend = _$httpBackend_;
			Machine = _Machine_;
            $sce = _$sce_;
            APIKey = _APIKey_;
            APIKey.set('yep123456789');
		}));

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

		
		it('test machine list', function(){
			defineUnitApiStub($httpBackend);
			                
			machineListResult = Machine.list(13);
			$httpBackend.flush();

			expect(machineListResult).toBeDefined();
			expect(machineListResult.error).toBeDefined();
			expect(machineListResult.error).toBe(500);
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
			
			$httpBackend.whenGET(/^testapi\/machines\/create\?cloudspaceId=0&name=test_create&description=Test\+Description&sizeId=1&imageId=2&disksize=3&archive=4&region=5&replication=6.*/).respond(200, 3);
			
			var machineCreateResult = Machine.create(0, 'test_create', 'Test Description', 1, 2, 3,4,5,6);
			
			$httpBackend.flush();

			expect(machineCreateResult).toBeDefined();
			expect(machineCreateResult.error).toBeUndefined();
			expect(machineCreateResult.id).toBe(3);
		});

		it('test machine create failure', function(){
			defineUnitApiStub($httpBackend);
			$httpBackend.whenGET(/^testapi\/machines\/create\?cloudspaceId=0&name=test_create_fail&description=Test\+Description&sizeId=0&imageId=0.*/).respond(500, -10);
		    
			var machineCreateResult = Machine.create(0, 'test_create_fail', 'Test Description', 0, 0);
			
			$httpBackend.flush();

			expect(machineCreateResult).toBeDefined();
			expect(machineCreateResult.error).toBe(500);
		});

		it('test machine delete', function() {
			defineUnitApiStub($httpBackend);

            var machineDeleteResult = Machine.delete(7);
            $httpBackend.flush();
            expect(machineDeleteResult.success).toBeDefined();
            expect(machineDeleteResult.success).toBe(true);

            var machines = Machine.list(0);
            $httpBackend.flush();

            expect(machines.error).toBeUndefined();
            expect(machines.length).toBeDefined();
            expect(_.where(machines, {id: 7})).toEqual([]);
        });

		it('test machine delete failure', function() {
			defineUnitApiStub($httpBackend);

            var machineDeleteResult = Machine.delete(2);
            $httpBackend.flush();
            expect(machineDeleteResult.success).toBeUndefined();
            expect(machineDeleteResult.error).toBeDefined();
            expect(machineDeleteResult.error).toBe(500);

            var machines = Machine.list(0);
            $httpBackend.flush();

            expect(machines.error).toBeUndefined();
            expect(machines.length).toBeDefined();
            expect(_.where(machines, {id: 2})).toEqual([]);
        });

		xit('test machine actions', function() {

		});

        it("retrieves the console URL", function() {
            defineUnitApiStub($httpBackend);
            var consoleUrlResult = Machine.getConsoleUrl(13);
            $httpBackend.flush();
            expect(consoleUrlResult.url).toEqual('http://www.reddit.com/');
        });

        it("can handle error returning the console URL", function() {
            defineUnitApiStub($httpBackend);
            var consoleUrlResult = Machine.getConsoleUrl(3);
            $httpBackend.flush();
            expect(consoleUrlResult.error).toBeDefined();
            expect(consoleUrlResult.url).toBeUndefined();
        });

		describe("snapshots", function() {
			it('can get list of snapshots for a certain machine', function() {
				defineUnitApiStub($httpBackend);

                var snapshotsResult = Machine.listSnapshots(7)
                $httpBackend.flush();

                expect(snapshotsResult.snapshots).toBeDefined();
                expect(snapshotsResult.snapshots.length).toBe(4);
                expect(snapshotsResult.snapshots).toEqual(['snap1', 'snap2', 'snap3', 'snap4']);
            });

            it('can create snapshot', function() {
				defineUnitApiStub($httpBackend);

                // Create a unique name so I don't create different snapshots with the same name
                var name = '7_snap_' + Math.random();
                var createSnapshotName = Machine.createSnapshot(7, name);
                $httpBackend.flush();
                expect(createSnapshotName.success).toBeDefined();
                expect(createSnapshotName.success).toBe(true);

                var snapshots = Machine.listSnapshots(7);
                $httpBackend.flush();
                expect(snapshots.snapshots).toBeDefined();
                expect(snapshots.snapshots).toContain(name);
            });

			it('can handle snapshot creation failure', function() {
				defineUnitApiStub($httpBackend);

                // Create a unique name so I don't create different snapshots with the same name
                var name = '2_snap_' + Math.random();
                var createSnapshotName = Machine.createSnapshot(2, name);
                $httpBackend.flush();
                expect(createSnapshotName.error).toBeDefined();
                expect(createSnapshotName.error).toBe(500);

                var snapshots = Machine.listSnapshots(2);
                $httpBackend.flush();
                expect(snapshots.snapshots).toBeDefined();
                expect(snapshots.snapshots).not.toContain(name);
            });
		});
	});

    describe('Sizes Service', function(){
		var $httpBackend, Sizes;

		beforeEach(inject(function(_$httpBackend_, _APIKey_, _Size_) {
			$httpBackend = _$httpBackend_;
            Size = _Size_;
            APIKey = _APIKey_;
            APIKey.set('yep123456789');
		}));

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

	describe("Images", function() {
		var $httpBackend, Image, APIKey;

		beforeEach(inject(function(_$httpBackend_, _Image_, _APIKey_) {
			$httpBackend = _$httpBackend_;
			Image = _Image_;
            APIKey = _APIKey_;
            APIKey.set('yep123456789');
		}));

	  	it('list', function() {
	  		defineUnitApiStub($httpBackend);
	  		var images = Image.list();
	  		$httpBackend.flush();
	  		expect(images.length).toBeDefined();
	  		expect(images.length).toBe(2);
	  	});
	});


});