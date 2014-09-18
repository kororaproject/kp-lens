var app = angular.module('lens-app', ['kp-lens']);

// call the python-webkit bridge
//app.run(function($rootScope) {
//});

function AppCtrl($scope) {
  $scope.hostname = 'unknown';

  /* SIGNALS */

  $scope.$on('update-config', function(e, hostname) {
    console.log(hostname);
    $scope.hostname = hostname;
  });

  $scope.updateHostname = function() {
    $scope.emitPYTHON('update-hostname', $scope.hostname);
  }

  $scope.closeApp = function() {
    $scope.emitPYTHON('close');
  }

  $scope.emitPYTHON('get-hostname');
}
