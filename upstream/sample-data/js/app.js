var app = angular.module('lens-app', ['lens.bridge', 'lens.ui']);

function AppCtrl($scope, $timeout) {
  $scope.hostname = 'unknown';
  $scope.foo = true;
  $scope.bar = 'green';
  $scope.progress = 0;

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

  $scope.updateProgress = function() {
    $scope.progress = Math.floor(Math.random() * 100);
    $timeout(function() { $scope.updateProgress(); }, 3000);
  };

  $scope.emit('get-hostname');

  $scope.updateProgress();
}
