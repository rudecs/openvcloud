describe("Machine buckets", function() {
    var $httpBackend, Buckets;
    
    beforeEach(module('myApp.services'));

    beforeEach(inject(function(_$httpBackend_) {
        $httpBackend = _$httpBackend_;
        inject(function($injector) {
            Buckets = $injector.get('Buckets');
        });        
    }));

    describe("creation", function() {
        var newBucket;
        beforeEach(function() {
            newBucket = new MachineBucket(Buckets,
            {
                id: Math.random() * 1000000000,
                ip: generateIp(),
                name: '',
                plan: {cpu: 1, memory: 1, storage: 10},
                additionalStorage: 12,
                
                region: [false, false, false],
                status: 'Running',
                image: '',
                history: [],
                snapshots: []
            });
        });

        it('adds a new bucket', function() {
            var numBefore = Buckets.getAll().length;
            newBucket.add();
            var numAfter = Buckets.getAll().length;
            expect(numAfter - numBefore).toBe(1);
        });

        it('sums all the storage', function() {
            expect(newBucket.storage).toBe(22);
        });

        it('creates a snapshot at creation', function() {
            newBucket.add();
            expect(newBucket.snapshots.length).toBe(1);
        });

        it('creates a backup at creation', function() {
            newBucket.add();
            expect(newBucket.history.length).toBe(1);
        });
    });

    describe("modification", function() {
        var bucket;
        beforeEach(function() {
            bucket = new MachineBucket(Buckets,
            {
                id: Math.random() * 1000000000,
                ip: generateIp(),
                name: '',
                plan: {cpu: 1, memory: 1, storage: 10},
                additionalStorage: 12,
                
                region: [false, false, false],
                status: 'Running',
                image: '',
                history: [],
                snapshots: []
            });
            bucket.add();
        });

        it('can retrieve saved bucket', function() {
            expect(Buckets.getById(bucket.id)).toBeDefined();
        });

        it("can boot", function() {
            bucket.boot();
            expect(bucket.status).toBe('Running');
        });

        it("can power-off", function() {
            bucket.powerOff();
            expect(bucket.status).toBe('Halted');
        });

        it("can pause", function() {
            bucket.pause();
            expect(bucket.status).toBe('Paused');
        });

        it("can be destroyed", function() {
            var numBeforeAnything = Buckets.getAll().length;
            
            bucket.add();
            var numAfterAddition = Buckets.getAll().length;
            expect(numAfterAddition - numBeforeAnything).toBe(1);
            
            bucket.remove();
            var numAfterDestroy = Buckets.getAll().length;
            expect(numAfterAddition - numAfterDestroy).toBe(1);
        });

        it('can change plan', function() {
            bucket.plan = {cpu: 2, memory: 8, storage: 15};
            expect(bucket.cpu).toBe(2);
            expect(bucket.memory).toBe(8);
            expect(bucket.storage).toBe(27);
        });

        describe("snapshots", function() {
            it('can create snapshot', function() {
                expect(bucket.snapshots.length).toBe(1); // The one created on bucket creation 
                bucket.createSnapshot("snapshot 1");
                expect(bucket.snapshots.length).toBe(2);
                expect(bucket.snapshots[1].name).toBe("snapshot 1");
            });

            it('when I restore from snapshot, it restores the plan to the plan of the snapshot', function() {
                expect(bucket.cpu).toBe(1);
                expect(bucket.memory).toBe(1);
                expect(bucket.storage).toBe(22);

                bucket.createSnapshot("snapshot 2");
                bucket.plan = {cpu: 2, memory: 8, storage: 15};
                bucket.restoreSnapshot(bucket.snapshots[1]);
                expect(bucket.cpu).toBe(1);
                expect(bucket.memory).toBe(1);
                expect(bucket.storage).toBe(22);
            });
          
        });

    });
});