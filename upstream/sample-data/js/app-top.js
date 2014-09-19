var app = angular.module('lens-app', ['lens-core']);

function AppCtrl($scope) {
  $scope.proc = {};

  /* SIGNALS */
  $scope.$on('update-proc', function(e, proc) {
    $scope.proc = proc;
  });

  $scope.closeApp = function() {
    $scope.emit('close');
  };

  $scope.emit('start-proc-watch');
}
