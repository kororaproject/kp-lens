var app = angular.module('lens-app', ['kp-lens']);

function AppCtrl($scope) {
  $scope.hostname = 'unknown';
  $scope.long_tasks = {};

  /* SIGNALS */
  $scope.$on('long-task-progress', function(e, uuid, p) {
    $scope.long_tasks[uuid] = p;
  });

  $scope.$on('long-task-complete', function(e, uuid, p) {
    $scope.long_tasks[uuid] = p;
  });

  $scope.$on('update-config', function(e, hostname) {
    console.log(hostname);
    $scope.hostname = hostname;
  });

  $scope.updateHostname = function() {
    $scope.emit('update-hostname', $scope.hostname);
  }

  $scope.startLongTask = function() {
    $scope.emit('start-long-task');
  }

  $scope.closeApp = function() {
    $scope.emit('close');
  }

  $scope.emit('get-hostname');
}
