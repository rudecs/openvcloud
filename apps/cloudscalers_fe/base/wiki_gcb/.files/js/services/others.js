'use strict';

///////////////////////////////////////////////////// Utilities ///////////////////////////////////////////////////// 
function generateIp() {
    return Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256) + '.' + Math.round(Math.random() * 1000 % 256);
}

// Creates a new object with the properties of all the objects passed. Last objects will override the first.
function mergeObjects() {
    var newObj = {};

    for (var i = 0; i < arguments.length; i++) {
        var obj = arguments[i];
        for (var attr in obj) {
            try {
                newObj[attr] = obj[attr];
            } catch (e) {}
        } 
    }
    return newObj;
}

///////////////////////////////////////////////////// Entities ///////////////////////////////////////////////////// 

function MachineBucket(backendService, props) {
    // Set attributes of the object
    for (var attr in props) {
        try {
            this[attr] = props[attr];
        } catch (e) {}
    }

    this.backendService = backendService;
}

MachineBucket.prototype.isValid = function() {
    return this.name && this.cpu && this.memory && this.storage && this.region && this.image;
}

MachineBucket.prototype.getSnapshot = function() {
    // $watch doesn't always update the values. This is why I need to recalculate here.
    return {
        name: this.name + '_' + getFormattedDate(),
        date: getFormattedDate(),
        cpu: this.plan.cpu,
        memory: this.plan.memory,
        storage: this.plan.storage,
        additionalStorage: this.additionalStorage
    };
}

MachineBucket.prototype.createSnapshot = function(snapshotName) {
    var snapshot = this.getSnapshot();
    snapshot.name = snapshotName;
    this.snapshots.push(snapshot);
    this.save();
}

MachineBucket.prototype.save = function() {
    this.backendService.save(this);
}

MachineBucket.prototype.add = function() {
    this.history.push({event: 'Created', initiated: getFormattedDate(), user: 'Admin'});
    this.snapshots.push(this.getSnapshot());
    this.backendService.add(this);
}

MachineBucket.prototype.boot = function() {
    this.status = 'Running';
    this.history.push({event: 'Started', initiated: getFormattedDate(), user: 'Admin'})
    this.save();
}

MachineBucket.prototype.powerOff = function() {
    this.status = 'Halted';
    this.history.push({event: 'Powered off', initiated: getFormattedDate(), user: 'Admin'})
    this.save();
};

MachineBucket.prototype.pause = function() {
    this.status = 'Paused';
    this.history.push({event: 'Paused', initiated: getFormattedDate(), user: 'Admin'})
    this.save();
};

MachineBucket.prototype.resize = function() {
    this.history.push({event: 'Bucket resized', initiated: getFormattedDate(), user: 'Admin'})
    this.save();
};

MachineBucket.prototype.remove = function() {
    this.backendService.remove(this);
};

MachineBucket.prototype.clone = function(cloneName) {
    this.backendService.add({
        id: Math.random() * 1000000000,
        ip: generateIp(),
        name: cloneName,
        plan: this.plan,
        additionalStorage: this.additionalStorage,
        region: this.region,
        status: 'Running',
        image: this.image,
        history: [{event: 'Created', initiated: getFormattedDate(), user: 'Admin'}]
    });
}

MachineBucket.prototype.restoreSnapshot = function(snapshot) {
    this.plan.cpu = snapshot.cpu;
    this.plan.memory = snapshot.memory;
    this.plan.storage = snapshot.storage;
    this.additionalStorage = snapshot.additionalStorage;
    this.save();
}

// The default way of creating computed properties in Angular is by using $scope.$watch. Computed properties belong to
// the model itself, not the controller.
Object.defineProperty(MachineBucket.prototype, 'cpu', {
    get: function() { return this.plan.cpu; }
});

Object.defineProperty(MachineBucket.prototype, 'memory', {
    get: function() { return this.plan.memory; }
});

Object.defineProperty(MachineBucket.prototype, 'storage', {
    get: function() { return this.plan.storage + this.additionalStorage; }
});

Object.defineProperty(MachineBucket.prototype, 'locations', {
    get: function() {
    // TODO: Get list of regions from a single source
    var self = this;
    return ["Ghent, Belgium", "Bruges, Belgium", "Lenoir, NC, USA"]
        .filter(function(element, index) { return self.region[index]; })
        .join(" - ");
}});

///////////////////////////////////////////////////// Services ///////////////////////////////////////////////////// 

function HttpService(entityName, Constructor, $http, additionalParams) {
    this.additionalParams = additionalParams;
    this.$http = $http;

    this.baseUrl = '/restmachine/cloudapi/' + entityName;

    this.getAll = function(params) {
        return this
            .$http({method: 'GET', url: this.baseUrl + '/list', params: mergeObjects(additionalParams, params)})
            .success(function(response) { 
                return response.map(function(elt) {
                    return new MachineBucket(elt); 
                }); 
            });
    };

    this.get = function(params) {
        return this.$http({method: 'GET', url: this.baseUrl + '/get', params: mergeObjects(additionalParams, params)});
    }
}

// Read & write JSON objects from/to localStorage
function LocalStorageService(keyName, Constructor) {
    this.keyName = keyName;

    this.getAll = function() {
        var all = [];
        if (localStorage.getItem(keyName))
            all = angular.fromJson(localStorage.getItem(keyName));
        if (Constructor) {   
            var service = this;
            all = all.map(function(e) { return new Constructor(service, e); });
        }
        return all;
    };

    this.saveAll = function(elements) {
        localStorage.setItem(keyName, angular.toJson(elements));
    };

    this.add = function(element) {
        var elements = this.getAll();
        elements.push(element);
        this.saveAll(elements);
    };

    this.getById = function(id) {
        var elements = this.getAll();
        for(var i = 0; i < elements.length; i++) {
            if (elements[i].id && elements[i].id === id)
                return elements[i];
        }
        return null;
    };

    this.save = function(element) {
        var elements = this.getAll();
        if (elements.length == 0) {
            this.add(element);
            return;
        }
        for(var i = 0; i < elements.length; i++) {
            if (elements[i].id && elements[i].id === element.id) {
                elements[i] = element;
                break;
            }
        }
        this.saveAll(elements);
    };

    this.remove = function(element) {
        var elements = this.getAll();
        elements.splice(elements.indexOf(element), 1);
        this.saveAll(elements);
    }
    return this;
}

angular.module('cloudscalers.services', ['ngResource'])
    .factory('Buckets', function($http) {
        //return new LocalStorageService('gcb-buckets', MachineBucket, $http);
        var Buckets = new HttpService('machines', MachineBucket, $http, {api_key: 'special-key', cloudspaceId: 1});

        Buckets.listSnapshots = function(params) {
            return this.$http({
                                method: 'GET', 
                                url: Buckets.baseUrl + '/listSnapshots',
                                params: mergeObjects(this.additionalParams, params)});
        };

        Buckets.createSnapshot = function(params) {
            return this.$http({
                                method: 'GET', 
                                url: Buckets.baseUrl + '/snapshot',
                                params: mergeObjects(this.additionalParams, params)});
        };
        
        return Buckets;
    })
    .factory('SettingsService', function($http) {
        return new LocalStorageService('gcb-settings', undefined, $http);
    })
    .factory('DesktopBucketService', function($http) {
        return new LocalStorageService('gcb-desktop-buckets', undefined, $http);
    })
    .factory('DNSService', function($http) {
        return new LocalStorageService('gcb-domains', undefined, $http);
    })
    .factory('SizesService', function($http) {
        return new HttpService('sizes', undefined, $http, {api_key: 'special-key'});
    });

