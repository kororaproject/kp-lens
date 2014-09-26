var app = angular.module('lens-app', ['lens.bridge', 'lens.ui']);

function AppCtrl($scope) {
  $scope.hostname = 'unknown';
  $scope.foo = true;
  $scope.bar = 're';
  $scope.progress = 32;

  /* SIGNALS */
  $scope.$on('update-config', function(e, hostname) {
    $scope.hostname = hostname;
  });

  $scope.updateHostname = function() {
    $scope.emit('update-hostname', $scope.hostname);
  };

  $scope.closeApp = function() {
    $scope.emit('close');
  };


  $scope.debug = function() {
    console.debug($scope.foo);
  };

  $scope.emit('get-hostname');
}
