angular.module('lens.bridge', []).
  run(function($rootScope) {
    $rootScope.emit = function() {
      window.lens.emit.apply(undefined, arguments);
    };

    $rootScope.safeApply = function(fn) {
      var phase = this.$root.$$phase;
      if (phase == '$apply' || phase == '$digest') {
        if(fn && (typeof(fn) === 'function')) {
          fn();
        }
      }
      else {
        this.$apply(fn);
      }
    };

    window.lens.on_any(function() {
      a = arguments;
      var _rs = angular.element(document).scope();
      _rs.safeApply(function(){
        _rs.$broadcast.apply(_rs, a)
      });
    });
  });

