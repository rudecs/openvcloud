'use strict';
module.exports = function(grunt) {
  return {
    options: {
      config: '.jscsrc',
      fix: true // Autofix code style violations when possible.
    },
    files: {
      src: ['.files/js/**/*.js']
    }
  };
};
