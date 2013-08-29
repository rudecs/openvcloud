'use strict';

function LocalStorageService(keyName) {
    this.keyName = keyName;

    this.getAll = function() {
        return angular.fromJson(localStorage.getItem(keyName));
    };

    this.saveAll = function(elements) {
        localStorage.setItem(keyName, angular.toJson(elements));
    };

    this.add = function(element) {
        var elements = this.getAll() || [];
        elements.push(element);
        this.saveAll(elements);
    }

    return this;
}


// Demonstrate how to register services
angular.module('myApp.services', [])
    .factory('Buckets', function() {
        return new LocalStorageService('gcb-buckets');
    });

