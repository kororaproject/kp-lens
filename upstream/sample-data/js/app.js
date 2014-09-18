var app = angular.module('lens-app', ['kp-lens']);

function AppCtrl($scope) {
  $scope.hostname = 'unknown';

  /* SIGNALS */
  $scope.$on('update-config', function(e, hostname) {
    $scope.hostname = hostname;
  });

  $scope.updateHostname = function() {
    $scope.emit('update-hostname', $scope.hostname);
  }

  $scope.closeApp = function() {
    $scope.emit('close');
  }

  $scope.emit('get-hostname');
}
