module.exports = function(grunt, config) {
  return {
    styles: {
      files: 'apps/ms1_fe/base/wiki_gcb/.files/less/*.less',
      tasks: [
        'less:all'
      ],
      options: {
        interrupt: true,
      }
    }
  };
};