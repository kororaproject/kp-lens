angular.module('lens-core', []).
  run(function($rootScope) {
    $rootScope.emit = function() {
      var _args = Array.prototype.slice.call(arguments);

      if( _args.length > 0 ) {
        var c = { name: _args.shift(), args: _args };

        /* update document title */
        var t = document.title;
        document.title = '_BR::' + angular.toJson(c, false);
        document.title = t;
      }
    };

    $rootScope.safeApply = function(fn) {
      var phase = this.$root.$$phase;
      if(phase == '$apply' || phase == '$digest') {
        if(fn && (typeof(fn) === 'function')) {
          fn();
        }
      }
      else {
        this.$apply(fn);
      }
    };
  });
