// Source: http://stackoverflow.com/a/901144
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function goHome() {
    window.location = '/gcb/buckets/';
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
        '2': 'Amsterdam 1', '3': 'San Francisco 1', '4': 'New York 2'
    };

    var images = {
        '350076': 'Ubuntu 13.04 x64',
        '345791': 'Ubuntu 13.04 x32',
        '473136': 'Ubuntu 12.10 x64 Desktop',
        '473123': 'Ubuntu 12.10 x64',
        '433240': 'Ubuntu 12.10 x32',
        '284203': 'Ubuntu 12.04 x64',
        '284211': 'Ubuntu 12.04 x32',
        '14097':  'Ubuntu 10.04 x64',
        '14098':  'Ubuntu 10.04 x32',
        '562354': 'CentOS 6.4 x64',
        '376568': 'CentOS 6.4 x32',
        '1601':   'CentOS 5.8 x64',
        '1602':   'CentOS 5.8 x32',
        '308287': 'Debian 7.0 x64',
        '303619': 'Debian 7.0 x32',
        '12573':  'Debian 6.0 x64',
        '12575':  'Debian 6.0 x32',
        '350424': 'Arch Linux 2013.05 x64',
        '361740': 'Arch Linux 2013.05 x32',
        '32419':  'Fedora 17 x64 Desktop',
        '32428':  'Fedora 17 x64',
        '32399':  'Fedora 17 x32 Desktop',
        '32387':  'Fedora 17 x32',
        '459444': 'LAMP on Ubuntu 12.04',
        '464235': 'Ruby on Rails on Ubuntu',
        '483575': 'Redmine on Ubuntu 12.04',
        '532043': 'Wordpress on Ubuntu 12.10',
        '599458': 'bala7-1375616079',
        '587173': 'testarvid.com 2013-08-02'
    };

    var Bucket = function(name, planId, regionId, imageId, virtIO, status) {
        var self = this;
        this.name = ko.observable(name);
        this.ip = ko.observable('192.241.173.134');
        this.status = ko.observable(status || 'active');

        this.planId = ko.observable(planId);
        this.memory = ko.computed(function() {
            return plans[self.planId()] ? plans[self.planId()].memory : '';
        });
        this.disk = ko.computed(function() {
            return plans[self.planId()] ? plans[self.planId()].disk : '';
        });

        this.regionId = ko.observable(regionId); 
        this.region = ko.computed(function() {
            return regions[self.regionId()] ? regions[self.regionId()] : '';
        });
        
        this.imageId = ko.observable(imageId);
        this.imageName = ko.computed(function() {
            return images[self.imageId()];
        });
        this.vertIO = ko.observable(virtIO);
        this.bucketUrl = ko.computed(function() {
            return "buckets/bucket?name=" + self.name();
        });

        this.history = ko.observableArray();

        this.snapshots = ko.computed(function(){
            /*return ko.utils.arrayFilter(viewModel.snapshots(), function(item){
                return item.name() === self.name();
            });*/
        });

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
            reload();
        }
    };

    var BucketHistory = function(event, initiated, execution) {
        var self = this;
        this.event = ko.observable(event);
        this.initiated = ko.observable(initiated);
        this.execution = ko.observable(execution);
    }

    var Snapshot = function(name, bucketName) {
        var self = this;
        this.name = ko.observable(name);
        this.bucketName = ko.observable(bucketName);
    }

    var ViewModel = function() {
        var self = this;
        this.username = ko.observable('Bob');
        //buckets: ko.observableArray(),
        if (!!localStorage.getItem(GCB_BUCKETS))
            this.buckets = ko.observableArray(ko.utils.arrayMap(
                                              ko.utils.parseJson(localStorage.getItem(GCB_BUCKETS)),
                                              function(bucket){
                                                return new Bucket(bucket.name, bucket.planId, bucket.regionId, bucket.imageId, bucket.vertIO, bucket.status);
                                              }));
        else
            this.buckets = ko.observableArray();

        // Used when creating a new bucket
        this.newBucket = ko.observable(new Bucket());

        this.saveBucket = function() {
            self.buckets.push(self.newBucket());
            self.newBucket(new Bucket());
            self.saveAllBuckets();
            goHome();
        }

        this.selectedBucket = ko.computed(function(){
            var bucketName = getParameterByName('name');
            for (var i = 0; i < self.buckets().length; i++) {
                if (self.buckets()[i].name() == bucketName)
                    return self.buckets()[i];
            }
            return new Bucket();
        });

        this.saveAllBuckets = function() {
            localStorage.setItem(GCB_BUCKETS, ko.toJSON(self.buckets));
        }

        this.snapshots = ko.observableArray();

        // internal ko.computed that saves buckets whenever they change
        ko.computed(function() {
            self.saveAllBuckets();
        }).extend({
            throttle: 500
        }); // save at most twice per second

        // Knockout doesn't handle when radio buttons are changed by JS, so I need to update viewModel on events
        $('.sizes-selection .size').on('click', function(){
            viewModel.newBucket().planId($(this).find('input').val());
        });
        $('.size').on('click', function() {
            $('.size').removeClass('selected');
            $(this).addClass('selected');
        });
        $('li.region input').on('click', function(){ 
            viewModel.newBucket().regionId($(this).val()) 
        });
        $('.tab-contents .radio_select').on('click', function(){ 
            viewModel.newBucket().imageId($(this).val()) 
        });
        $('#action-select > ul > li > a').on('click', function(){
            $($(this).attr('href') + ' a:first').click();
            console.log($(this).attr('href'));
        });
    };

    var viewModel = window.viewModel = new ViewModel();

    ko.applyBindings(viewModel);
});
