var app = angular.module('lens-app', ['lens.bridge', 'lens.ui']);

app.controller('AppCtrl', function($scope) {
  $scope.hostname = 'unknown';
  $scope.long_tasks = {};

  /* SIGNALS */
  $scope.$on('long-task-progress', function(e, uuid, p) {
    $scope.long_tasks[uuid] = p;
  });

  $scope.$on('long-task-complete', function(e, uuid, p) {
    $scope.long_tasks[uuid] = 100;
  });

  $scope.$on('update-config', function(e, hostname) {
    console.log(hostname);
    $scope.hostname = hostname;
  });

  $scope.startLongTask = function() {
    $scope.emit('start-long-task');
  }

  $scope.closeApp = function() {
    $scope.emit('close');
  }

  $scope.emit('get-hostname');
});
