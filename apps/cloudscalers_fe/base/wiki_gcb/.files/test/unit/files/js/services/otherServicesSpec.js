describe("Machine buckets", function() {
    var $httpBackend, Buckets;
    
    beforeEach(module('myApp.services'));

    beforeEach(inject(function(_$httpBackend_, $injector) {
        $httpBackend = _$httpBackend_;
        Buckets = $injector.get('Buckets');
        defineMachineBucketsStubInLocalStorage($httpBackend);
    }));


    xdescribe("creation", function() {
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
        it('can retrieve list of buckets', function() {    
            var buckets = Buckets.getAll();
            expect(buckets.length).toBe(0);
            $httpBackend.flush();
            expect(buckets.length).toBe(2);
        });

        it('can retrieve saved bucket', function() {
            var bucket = Buckets.get({machineId: 1});
            $httpBackend.flush();
            expect(bucket).toBeDefined();
            expect(bucket.id).toBe(1);
            expect(bucket.name).toBe('Machine 1');
        });

        xit("can boot", function() {
            bucket.boot();
            expect(bucket.status).toBe('Running');
        });

        xit("can power-off", function() {
            bucket.powerOff();
            expect(bucket.status).toBe('Halted');
        });

        xit("can pause", function() {
            bucket.pause();
            expect(bucket.status).toBe('Paused');
        });

        xit("can be destroyed", function() {
            var numBeforeAnything = Buckets.getAll().length;
            
            bucket.add();
            var numAfterAddition = Buckets.getAll().length;
            expect(numAfterAddition - numBeforeAnything).toBe(1);
            
            bucket.remove();
            var numAfterDestroy = Buckets.getAll().length;
            expect(numAfterAddition - numAfterDestroy).toBe(1);
        });

        xit('can change plan', function() {
            bucket.plan = {cpu: 2, memory: 8, storage: 15};
            expect(bucket.cpu).toBe(2);
            expect(bucket.memory).toBe(8);
            expect(bucket.storage).toBe(27);
        });

        xit('can be cloned', function() {
            var numBucketsBefore = Buckets.getAll().length;
            bucket.clone('Clone 1');
            var buckets = Buckets.getAll();
            var numBucketsAfter = buckets.length;
            expect(numBucketsAfter - numBucketsBefore).toBe(1);
            expect(buckets[buckets.length - 1].name).toBe('Clone 1');
        });

        describe("snapshots", function() {
            it('can get list of snapshots for a certain machine', function() {
                var snapshots = Buckets.listSnapshots({machineId: 7});
                $httpBackend.flush();
                console.log(snapshots);
                expect(snapshots.length).toBe(4);
            });
            xit('can create snapshot', function() {
                expect(bucket.snapshots.length).toBe(1); // The one created on bucket creation 
                bucket.createSnapshot("snapshot 1");
                expect(bucket.snapshots.length).toBe(2);
                expect(bucket.snapshots[1].name).toBe("snapshot 1");
            });

            xit('when I restore from snapshot, it restores the plan to the plan of the snapshot', function() {
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

describe("Sizes", function() {
    var $httpBackend, Sizes;
    beforeEach(module('myApp.services'));

    beforeEach(inject(['$httpBackend', 'SizesService', function(_$httpBackend_, _Sizes_) {
        $httpBackend = _$httpBackend_;
        Sizes = _Sizes_;
        defineMachineBucketsStubInLocalStorage($httpBackend);
    }]));


    it('should return a list of sizes', function() {
        var sizes = Sizes.getAll();
        $httpBackend.flush();
        expect(sizes.length).toBe(3);
    })
});

describe("mergeObjects", function() {
    it('Should create a single object with all properties of the given objects. Later parameters override earlier ones', function() {
        expect(mergeObjects({a: 1, b: 2}, {a: 3, c: 14})).toEqual({a: 3, c: 14, b: 2});
    })
});