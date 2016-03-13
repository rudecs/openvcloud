'use strict';

module.exports = function(grunt) {
  var config = grunt.file.readJSON('./grunt/config.json');

  function loadGruntTask(name) {
    return require('./grunt/' + name)(grunt, config);
  }

  // plugins
  require('load-grunt-tasks')(grunt);
  
  // configurations
  grunt.initConfig({
    less: loadGruntTask('less'),
    watch: loadGruntTask('watch')
  });

  grunt.registerTask('build', [
    'less:all'
  ]);

  grunt.registerTask('develop', [
    'build',
    'watch'
  ]);

  grunt.registerTask('default', [
    'develop'
  ]);  
};