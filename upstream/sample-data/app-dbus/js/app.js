var app = angular.module('lens-app', ['lens.bridge', 'lens.ui']);

app.controller('AppCtrl', function($scope, $timeout) {
  $scope.hostname = 'unknown';
  $scope.foo = true;
  $scope.bar = 'green';
  $scope.progress = 0;
  $scope.maximizeButtonText = "Maximize";
  $scope.fullscreenButtonText = "Fullscreen";

  /* SIGNALS */
  $scope.$on('update-config', function(e, hostname) {
    $scope.hostname = hostname;
  });

  $scope.$on('window-maximized', function(e) {
    $scope.maximizeButtonText = "Unmaximize";
  });

  $scope.$on('window-unmaximized', function(e) {
    $scope.maximizeButtonText = "Maximize";
  });

  $scope.$on('window-fullscreen', function(e) {
    $scope.fullscreenButtonText = "Exit Fullscreen";
  });

  $scope.$on('window-unfullscreen', function(e) {
    $scope.fullscreenButtonText = "Fullscreen";
  });


  /* SCOPE METHODS */
  $scope.updateHostname = function() {
    $scope.emit('update-hostname', $scope.hostname);
  };

  $scope.maximize = function() {
    $scope.emit('toggle-window-maximize');
  };

  $scope.fullscreen = function() {
    $scope.emit('toggle-window-fullscreen');
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
});
