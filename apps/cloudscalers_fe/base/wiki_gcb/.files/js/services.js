'use strict';

// Read & write JSON objects from/to localStorage
function LocalStorageService(keyName) {
    this.keyName = keyName;

    this.getAll = function() {
        if (localStorage.getItem(keyName))
            return angular.fromJson(localStorage.getItem(keyName));
        else
            return [];
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

angular.module('myApp.services', [])
    .factory('Buckets', function() {
        return new LocalStorageService('gcb-buckets');
    })
    .factory('Snapshots', function() {
        return new LocalStorageService('gcb-snapshots');
    })
    .factory('SettingsService', function() {
        return new LocalStorageService('gcb-settings');
    })
    .factory('DesktopBucketService', function() {
        return new LocalStorageService('gcb-desktop-buckets');
    });

