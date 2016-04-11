'use strict';

module.exports = function(grunt) {

  function loadGruntTask(name) {
    return require('./GruntTasks/' + name)(grunt);
  }

  // plugins
  require('load-grunt-tasks')(grunt);

  // configurations
  grunt.initConfig({
    less: loadGruntTask('less'),
    watch: loadGruntTask('watch'),
    jshint: loadGruntTask('jshint'),
    jscs: loadGruntTask('jscs')
  });

  grunt.registerTask('build', [
    'less:all'
  ]);

  grunt.registerTask('lint', [
    'jshint',
    'jscs'
  ]);

  grunt.registerTask('develop', [
    'build',
    'lint',
    'watch'
  ]);

  grunt.registerTask('default', [
    'develop'
  ]);
};
