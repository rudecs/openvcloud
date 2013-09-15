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
        })
    });
});