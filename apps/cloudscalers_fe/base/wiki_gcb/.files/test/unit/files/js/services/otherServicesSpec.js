xdescribe("Machine buckets", function() {
    var $httpBackend, Buckets;
    
    beforeEach(module('cloudscalers.services'));

    beforeEach(inject(function(_$httpBackend_, _Buckets_, _$rootScope_) {
        $httpBackend = _$httpBackend_;
        Buckets = _Buckets_;
        $rootScope = _$rootScope_;
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
            Buckets.getAll().success(function(buckets) {
                expect(buckets.length).toBe(2);
            });
            $httpBackend.flush();
        });

        it('can retrieve saved bucket', function() {
            Buckets.get({machineId: 1}).success(function(bucket) {
                expect(bucket).toBeDefined();
                expect(bucket.id).toBe(1);
                expect(bucket.name).toBe('Machine 1');
            });
            $httpBackend.flush();
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

        xdescribe("snapshots", function() {
            xit('can get list of snapshots for a certain machine', function() {
                Buckets.listSnapshots({machineId: 7}).success(function(snapshots) {
                    expect(snapshots.length).toBe(4);
                    expect(snapshots).toEqual(['snap1', 'snap2', 'snap3', 'snap4']);
                });
                $httpBackend.flush();
            });
            xit('can create snapshot', function() {
                // Create a unique name so I don't create different snapshots with the same name
                var name = '7_snap_' + Math.random();

                Buckets.listSnapshots({machineId: 7}).success(function(snapshotsBefore) {
                    /*Buckets.createSnapshot({machineId: 7, name: name}).success(function(name) {
                        console.log(name);
                        Buckets.listSnapshots({machineId: 7}).success(function(snapshotsAfter) {
                            expect(snapshotsBefore.length - snapshotsAfter.length).toBe(1);
                            expect(snapshotsAfter).toContain(name);
                        });
                        $httpBackend.flush();
                    });
                    $httpBackend.flush();*/
                });
                $httpBackend.flush();
            });

            xit('when I restore from snapshot, it restores the plan to the plan of the snapshot', function() {
                expect(bucket.cpu).toBe(1);
                expect(bucket.memory).toBe(1);
                expect(bucket.storage).toBe(22);

                bucket.createSnapshot("snapshot 2");
                bucket.plan = {cpu: 2, memory: 8, storage: 15};
                bucket.rollbackSnapshot(1, bucket.snapshots[1]);
                expect(bucket.cpu).toBe(1);
                expect(bucket.memory).toBe(1);
                expect(bucket.storage).toBe(22);
            });
        });
    });
});

xdescribe("Sizes", function() {
    var $httpBackend, Sizes;
    beforeEach(module('cloudscalers.services'));

    beforeEach(inject(function(_$httpBackend_, SizesService) {
        $httpBackend = _$httpBackend_;
        Sizes = SizesService;
        defineMachineBucketsStubInLocalStorage($httpBackend);
    }));


    it('should return a list of sizes', function() {
        Sizes.getAll().success(function(sizes) {
            expect(sizes.length).toBe(3);
        });
        $httpBackend.flush();
    })
});

xdescribe("mergeObjects", function() {
    it('Should create a single object with all properties of the given objects. Later parameters override earlier ones', function() {
        expect(mergeObjects({a: 1, b: 2}, {a: 3, c: 14})).toEqual({a: 3, c: 14, b: 2});
    })
});