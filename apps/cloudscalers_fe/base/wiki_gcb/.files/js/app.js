// Source of this function: http://stackoverflow.com/a/901144
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function goHome() {
    window.location = '/test_gcb/buckets_list';
}

function reload() {
    window.location.reload();
}

jQuery(function(){

    var GCB_BUCKETS = 'gcb-buckets';

    var plans = {
        '66': {'memory': '512MB',  'disk': '20GB'},
        '63': {'memory': '1GB',    'disk': '30GB'},
        '62': {'memory': '2GB',    'disk': '40GB'},
        '64': {'memory': '4GB',    'disk': '60GB'},
        '65': {'memory': '8GB',    'disk': '80GB'},
        '61': {'memory': '16GB',   'disk': '160GB'},
        '60': {'memory': '32GB',   'disk': '320GB'},
        '70': {'memory': '48GB',   'disk': '480GB'},
        '69': {'memory': '64GB',   'disk': '640GB'},
        '68': {'memory': '96GB',   'disk': '960GB'},
    };

    var regions = {
        '2': 'Region 1', '3': 'Region 2', '4': 'Region 3'
    };

    var images = {
        '1': 'Image 1',
        '2':  'Image 2',
    };

    var Bucket = function(id, name, plan, region, imageName, status) {
        var self = this;
        this.id = ko.observable(id || (Math.random() * 1000000000));
        this.name = ko.observable(name);
        this.status = ko.observable(status || 'active');

        this.plan = ko.observable(plan);

        this.region = ko.observable(region);
        
        this.imageName = ko.observable(imageName);
        this.bucketUrl = ko.computed(function() {
            return "/test_gcb/bucket?id=" + self.id();
        });

        this.history = ko.observableArray();
        self.history.push(new BucketHistory('Created', new Date(), '15 seconds'));

        this.powerOffBucket = function() {
            self.status('off');
            viewModel.saveAllBuckets();
            self.history.push(new BucketHistory('Powered off', new Date(), '5 seconds'));
        };

        this.bootBucket = function() {
            self.status('active');
            viewModel.saveAllBuckets();
            self.history.push(new BucketHistory('Started', new Date(), '15 seconds'));
        };

        this.destroy = function() {
            viewModel.buckets.remove(self);
            viewModel.saveAllBuckets();
            goHome();
        }

        this.resize = function() {
            viewModel.saveAllBuckets();
            self.history.push(new BucketHistory('Plan changed to ' + self.plan(), new Date(), '15 seconds'));
        }
    };

    var BucketHistory = function(event, initiated, execution) {
        var self = this;
        this.event = ko.observable(event);
        this.initiated = ko.observable(initiated);
        this.execution = ko.observable(execution);
    }

    var Snapshot = function(name, bucketId) {
        var self = this;
        this.name = ko.observable(name);
        this.bucketId = ko.observable();
    }

    var ViewModel = function() {
        var self = this;
        this.username = ko.observable('Bob');
        if (!!localStorage.getItem(GCB_BUCKETS))
            this.buckets = ko.observableArray(ko.utils.arrayMap(
                                              ko.utils.parseJson(localStorage.getItem(GCB_BUCKETS)),
                                              function(bucket){
                                                return new Bucket(bucket.id, bucket.name, bucket.plan, bucket.region, bucket.imageName, bucket.status);
                                              }));
        else
            this.buckets = ko.observableArray();

        // Used when creating a new bucket
        this.newBucket = ko.observable(new Bucket());

        this.saveBucket = function() {
            if (self.buckets.indexOf(self.selectedBucket()) == -1)
                self.buckets.push(self.newBucket());

            self.newBucket(new Bucket());
            self.saveAllBuckets();
            goHome();
        }

        this.selectedBucket = ko.computed(function(){
            var bucketId = getParameterByName('id');
            for (var i = 0; i < self.buckets().length; i++) {
                if (self.buckets()[i].id() == bucketId)
                    return self.buckets()[i];
            }
            return self.newBucket();
        });

        this.saveAllBuckets = function() {
            localStorage.setItem(GCB_BUCKETS, ko.toJSON(self.buckets));
        };

        if (!!localStorage.getItem('gcb-snapshots'))
            this.snapshots = ko.observableArray(ko.utils.arrayMap(
                                                ko.utils.parseJson(localStorage.getItem('gcb-snapshots')),
                                                function(snap) {
                                                    var snapshot = new Snapshot();
                                                    snapshot.bucketId(snap.bucketId);
                                                    snapshot.name(snap.name);
                                                    return snapshot;
                                                }));
        else
            this.snapshots = ko.observableArray();

        this.newSnapshot = ko.observable(new Snapshot());
        this.saveSnapshot = function() {
            self.newSnapshot().bucketId(self.selectedBucket().id());
            self.snapshots.push(self.newSnapshot());
            self.newSnapshot(new Snapshot());
            localStorage.setItem('gcb-snapshots', ko.toJSON(self.snapshots));
        };

        this.restoreSnapshot = function() {
            reload();
        };
        
        // internal ko.computed that saves buckets whenever they change
        ko.computed(function() {
            self.saveAllBuckets();
        }).extend({
            throttle: 500
        }); // save at most twice per second
    };

    var viewModel = window.viewModel = new ViewModel();

    ko.applyBindings(viewModel);
});
