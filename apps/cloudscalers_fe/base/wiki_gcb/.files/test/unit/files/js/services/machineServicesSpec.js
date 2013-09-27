describe('Cloudscalers machine services', function() {


	beforeEach(module('cloudscalers.machineServices'));
	
	describe('User service', function(){
		var $httpBackend, User;
		beforeEach(inject(function(_$httpBackend_, _User_) {
			$httpBackend = _$httpBackend_;
			User = _User_;
		}));
		
		xit('Login succeeds',function(){			
			defineUnitApiStub($httpBackend);

			var loginResult = User.login();

			$httpBackend.flush();
			
			expect(loginResult.username).toBe('testuser');
			expect(loginResult.authKey).toBe('yep123456789');
			expect(loginResult.error).toBeUndefined();
		});
		
		xit('Login fails',function(){
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

		beforeEach(inject(function(_$httpBackend_, _Machine_) {
			$httpBackend = _$httpBackend_;
			Machine = _Machine_;
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
			var machineCreateResult = Machine.create(0, 'test_create', 'Test Description', 0, 0);
                            //expect(machineCreateResult.id).toBeUndefined();
			
			$httpBackend.flush();

			expect(machineCreateResult).toBeDefined();
			expect(machineCreateResult.error).toBeUndefined();
			expect(machineCreateResult.id).toBe(3);
		});

		it('test machine create failure', function(){
			defineUnitApiStub($httpBackend);
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
                var snapshotName = '7_snap_' + Math.random();
                var createSnapshotName = Machine.createSnapshot(7, snapshotName);
                $httpBackend.flush();
                expect(createSnapshotName.success).toBeDefined();
                expect(createSnapshotName.success).toBe(true);

                var snapshots = Machine.listSnapshots(7);
                $httpBackend.flush();
                expect(snapshots.snapshots).toBeDefined();
                expect(snapshots.snapshots).toContain(snapshotName);
            });

			it('can handle snapshot creation failure', function() {
				defineUnitApiStub($httpBackend);

                // Create a unique name so I don't create different snapshots with the same name
                var snapshotName = '2_snap_' + Math.random();
                var createSnapshotName = Machine.createSnapshot(2, snapshotName);
                $httpBackend.flush();
                expect(createSnapshotName.error).toBeDefined();
                expect(createSnapshotName.error).toBe(500);

                var snapshots = Machine.listSnapshots(2);
                $httpBackend.flush();
                expect(snapshots.snapshots).toBeDefined();
                expect(snapshots.snapshots).not.toContain(snapshotName);
            });
		});

			
		
	});

    describe('Sizes Service', function(){
		var $httpBackend, Sizes;

		beforeEach(inject(function(_$httpBackend_) {
			$httpBackend = _$httpBackend_;
			
			inject(function($injector) {
			    Size = $injector.get('Size');
			});
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
		var $httpBackend, Image;

		beforeEach(inject(function(_$httpBackend_, _Image_) {
			$httpBackend = _$httpBackend_;
			Image = _Image_;
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