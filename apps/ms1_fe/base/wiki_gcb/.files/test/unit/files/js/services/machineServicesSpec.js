describe('Cloudscalers machine services', function() {
	beforeEach(module('cloudscalers.services'));
	
	describe('Machine Service', function(){
		var $httpBackend, $sce, Machine;

		beforeEach(inject(function(_$httpBackend_, _$sce_, _Machine_) {
			$httpBackend = _$httpBackend_;
			Machine = _Machine_;
            $sce = _$sce_;
		}));

		it('test machine list', function(){
			defineUnitApiStub($httpBackend);
			
			var machineListResult
			
			Machine.list(0).then(function(result){machineListResult = result;},function(reason){})
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
		    $httpBackend.whenGET(/^testapi\/machines\/get\?machineId=44534(&api_ke.*)?/).respond(500, 'Not Found');
			
		    machineGetErrorResult = Machine.get(44534);
			$httpBackend.flush();

			expect(machineGetErrorResult).toBeDefined();
			expect(machineGetErrorResult.error).toBe(500);
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
		});
	});

    describe('Sizes Service', function(){
		var $httpBackend, Sizes;

		beforeEach(inject(function(_$httpBackend_, _Size_) {
			$httpBackend = _$httpBackend_;
            Size = _Size_;
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