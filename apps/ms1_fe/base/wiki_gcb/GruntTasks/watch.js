module.exports = function(grunt) {
  return {
    styles: {
      files: ['.files/less/*.less', '.files/js/**/*.js'],
      tasks: [
        'less:all',
        'jshint',
        'jscs'
      ],
      options: {
        interrupt: true,
      }
    }
  };
};
