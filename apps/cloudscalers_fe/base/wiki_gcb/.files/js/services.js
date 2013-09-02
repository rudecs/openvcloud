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
    }

    return this;
}


angular.module('myApp.services', [])
    .factory('Buckets', function() {
        return new LocalStorageService('gcb-buckets');
    });

