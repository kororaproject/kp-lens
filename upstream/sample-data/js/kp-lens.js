angular.module('kp-lens', []).
run(function($rootScope) { 
  $rootScope.emitPYTHON = function() {
    var _args = Array.prototype.slice.call(arguments);

    if( _args.length > 0 ) {
      var _command = {
        name: _args.shift(),
        args: _args
      }

      /* update document title */
      var _title = document.title;
      document.title = '_BR::' + angular.toJson(_command, false);
      document.title = _title;
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
