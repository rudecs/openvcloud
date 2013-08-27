// Source of this function: http://stackoverflow.com/a/901144
function getParameterByName(name) {
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function goHome() {
    window.location = '/test_gcb/buckets';
}

function reload() {
    window.location.reload();
}

jQuery(function(){
    // require KnockoutJS, jQuery.validate, Knockout.validation
    var GCB_BUCKETS = 'gcb-buckets';

    var Bucket = function(params) {
        var self = this;
        this.id = ko.observable(Math.random() * 1000000000);
        this.name = ko.observable();
        this.status = ko.observable('active');

        this.plan = ko.observable();

        this.region = ko.observable();
        
        this.imageName = ko.observable();
        this.bucketUrl = ko.computed(function() {
            return "/test_gcb/bucket?id=" + self.id();
        });

        this.valid = ko.computed(function(){
            return !!(self.name() && self.plan() && self.region() && self.imageName());
        });

        for (var attr in params) {
            try {
                this[attr](params[attr]);
            } catch (e) {}
        }

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
    };

    function bufferedObservable(initialValue) {
        var property = ko.observable(initialValue);
        property.tempValue = initialValue;
        property.buffer = ko.computed({
            read: function() { 
                property.tempValue = property();
                return property();
            },
            write: function(value) {
                property.tempValue = value;
            }
        });

        property.commit = function() {
            property(property.tempValue);
        }
        return property;
    };

    var SSHKey = function() {
        var self = this;
        this.name = bufferedObservable();
        this.key = bufferedObservable();

        this.editing = ko.observable(false);

        this.destroy = function() {
            viewModel.sshKeys.remove(self);
            localStorage.setItem('gcb-sshKeys', ko.toJSON(self.sshKeys));
        };

        this.startEditing = function() {
            this.editing(true);
        };

        this.stopEditing = function() {
            this.editing(false);
        };

        this.save = function() {
            self.name.commit();
            self.key.commit();
            self.stopEditing();
        };
    };

    var ViewModel = function() {
        var self = this;
        this.username = ko.observable('Bob');
        if (!!localStorage.getItem(GCB_BUCKETS))
            this.buckets = ko.observableArray(ko.utils.arrayMap(
                                              ko.utils.parseJson(localStorage.getItem(GCB_BUCKETS)),
                                              function(bucket){
                                                return new Bucket(bucket);
                                              }));
        else
            this.buckets = ko.observableArray();

        // ================ Buckets =======================
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

        // ================ Snapshots =======================
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

        // ================ SSH Keys =======================
        if (!!localStorage.getItem('gcb-sshKeys'))
            this.sshKeys = ko.observableArray(ko.utils.arrayMap(
                                                ko.utils.parseJson(localStorage.getItem('gcb-sshKeys')),
                                                function(key) {
                                                    var sshKey = new SSHKey();
                                                    sshKey.name(key.name);
                                                    sshKey.key(key.key);
                                                    return sshKey;
                                                }));
        else
            this.sshKeys = ko.observableArray();
        this.newSSHKey = ko.observable(new SSHKey());
        this.addSSHKey = function() {
            this.sshKeys.push(self.newSSHKey());
            this.newSSHKey(new SSHKey());
            $('.popup-background').parent().hide();
        };

        this.enableVirtIO = ko.observable(true);

        // ====================== DNS Record
        var DNSRecord = function(params) {
            var self = this;
            this.type = ko.observable(); // A, NS, CNAME
            this.name = ko.observable();
            this.hostname = ko.observable();
            this.ipAddress = ko.observable();
            this.priority = ko.observable();
            this.text = ko.observable();
            this.port = ko.observable();
            this.weight = ko.observable();

            // update attributes from the passed object
            for (var attr in params) {
                try {
                    this[attr](params[attr]);
                } catch (e) {}
            };

            this.valid = function() {
                if (self.type() == 'A')
                    return !! (self.name() && self.ipAddress());
                else if (self.type() == 'NS')
                    return !! self.hostname();
                else if (self.type() == 'CNAME')
                    return !! (self.name() && self.hostname());
                return false;
            };
        };

        var DNSDomain = function(params) {
            var self = this;
            this.name = ko.observable();
            this.bucket = ko.observable();
            this.records = ko.observableArray([
                new DNSRecord({type: 'A', name: '@', ipAddress: '10.10.10.10'}),
                new DNSRecord({type: 'NS', hostname: 'ns1.oursite.com'}),
                new DNSRecord({type: 'NS', hostname: 'ns2.oursite.com'})
            ]);
            for (var attr in params) {
                try {
                    this[attr](params[attr]);
                } catch (e) {}
            }
            this.newRecord = ko.observable(new DNSRecord({}));
            this.addRecord = function() {
                self.records.push(self.newRecord());
                self.newRecord(new DNSRecord({}));
            };

            this.remove = function() {
                viewModel.domains.remove(self);
                localStorage.setItem('gcb-domains', ko.toJSON(self.domains));
            };

            this.removeRecord = function(record) {
                self.records.remove(record);
                localStorage.setItem('gcb-domains', ko.toJSON(viewModel.domains));
            };
        };

        if (!!localStorage.getItem('gcb-domains'))
        {
            this.domains = ko.observableArray(ko.utils.arrayMap(
                                                ko.utils.parseJson(localStorage.getItem('gcb-domains')),
                                                function(key) {
                                                    var domain = new DNSDomain(key);
                                                    domain.bucket(new Bucket(key.bucket));
                                                    domain.records(ko.utils.arrayMap(key.records, function(rec) { return new DNSRecord(rec); }))
                                                    return domain;
                                                }));
        }
        else
            this.domains = ko.observableArray();

        this.newDomain = ko.observable(new DNSDomain());
        this.addDomain = function() {
            self.domains.unshift(self.newDomain());
            self.newDomain(new DNSDomain());
        };

        var LoginModel = function() {
            var self = this;
            this.username = ko.observable();
            this.password = ko.observable();

            this.login = function() {
                if (self.username() === 'admin' && self.password() === '123')
                    location.href = '/test_gcb/buckets';
                else
                    $('.alert-error').show('fast');
            };
        };

        this.loginModel = new LoginModel();
        
        // internal ko.computed that saves buckets whenever they change
        ko.computed(function() {
            self.saveAllBuckets();
            localStorage.setItem('gcb-sshKeys', ko.toJSON(self.sshKeys));
            localStorage.setItem('gcb-domains', ko.toJSON(self.domains));
        }).extend({
            throttle: 500
        }); // save at most twice per second
    };

    var viewModel = window.viewModel = new ViewModel();

    ko.applyBindings(viewModel);


    // Popups
    $('.popup-show').on('click', function(e) {
        e.preventDefault();
        $($(this).attr('href')).toggle('fast');
    });
    $('.popup-background').on('click', function() {
        $(this).parent().hide();
    });
    $('.popup-content').on('click', function(e) {
        e.stopPropagation();
    });

    // When radio buttons inside li.shortcut is selected, make the whole li selected, for better UI
    function selectParent() {
        var btn = $(this);
        btn.parents('.shortcuts').find('li.shortcut').removeClass('selected');
        if (btn.attr('checked'))
            btn.parents('.shortcut').addClass('selected');
    };
    $('.shortcut > input[type=radio]').on('change', selectParent);
    $('.shortcut > input[type=radio]:checked').each(selectParent);


    // Context-menu on buckets list
    $(function(){
        $('#machine_buckets > tbody > tr').contextMenu({
            selector: 'tr', 
            callback: function(key, options) {
                var m = "clicked: " + key + " on " + $(this).text();
                window.console && console.log(m) || alert(m); 
            },
            items: {
                "edit": {name: "Edit", icon: "edit"},
                "cut": {name: "Cut", icon: "cut"},
                "copy": {name: "Copy", icon: "copy"},
                "paste": {name: "Paste", icon: "paste"},
                "delete": {name: "Delete", icon: "delete"},
                "sep1": "---------",
                "quit": {name: "Quit", icon: "quit"}
            }
        });
    });
});

