module.exports = function(grunt) {
  return {
    options: {
      jshintrc: '.jshintrc'
    },
    all: ['Grunfile.js', '.files/js/**/*.js']
  };
};
