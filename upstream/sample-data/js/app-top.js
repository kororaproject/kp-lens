var app = angular.module('lens-app', ['lens.bridge', 'lens.ui']);

app.controller('AppCtrl', function($scope) {
  $scope.proc = [
    {'pid': 16064, 'priority': 20, 'cmdline': '/opt/google/chrome/chrome --type=renderer --enable-deferred-image-decoding --lang=en-GB --force-fieldtrials=AutoReloadExperiment/Enabled/AutoReloadVisibleOnlyExperiment/Enabled/ChromeSuggestions/Most Likely with Kodachrome/ExtensionInstallVerification/None/OmniboxBundledExperimentV1/StandardR4/Prerender/PrerenderEnabled/PrerenderLocalPredictorSpec/LocalPredictor=Disabled/QUIC/Disabled/SDCH/EnabledAll/SafeBrowsingIncidentReportingService/Default/SettingsEnforcement/no_enforcement/Test0PercentDefault/group_01/UMA-Dynamic-Binary-Uniformity-Trial/default/UMA-New-Install-Uniformity-Trial/Control/UMA-Population-Restrict/normal/UMA-Session-Randomized-Uniformity-Trial-5-Percent/default/UMA-Uniformity-Trial-1-Percent/group_99/UMA-Uniformity-Trial-10-Percent/group_06/UMA-Uniformity-Trial-100-Percent/group_01/UMA-Uniformity-Trial-20-Percent/group_04/UMA-Uniformity-Trial-5-Percent/default/UMA-Uniformity-Trial-50-Percent/default/VoiceTrigger/Install/ --renderer-print-preview --enable-offline-auto-reload --enable-offline-auto-reload-visible-only --enable-threaded-compositing --enable-delegated-renderer --enable-impl-side-painting --disable-accelerated-video-decode --channel=15736.22.1197994179', 'state': 'S', 'comm': '(chrome)', 'ppid': 15758, 'nice': 0}
  ];

  $scope.headers = [
    { key: 'pid',      label: 'PID' },
    { key: 'ppid',     label: 'PPID' },
    { key: 'ppid',     label: 'USER' },
    { key: 'nice',     label: 'NI' },
    { key: 'priority', label: 'PR' },
    { key: 'vsize',   label: 'VIRT' },
    { key: 'mem_resident',   label: 'RES' },
    { key: 'mem_shared', label: 'SHR' },
    { key: 'state', label: 'S' },
    { key: 'status', label: 'CPU' },
    { key: 'mem_percentage', label: 'MEM' },
    { key: 'status', label: 'TIME' },
    { key: 'cmdline',  label: 'Command' },
  ];

  $scope.sort = {
    column: 'b',
    descending: false
  };

  $scope.selectedCls = function(column) {
    return column == $scope.sort.column && 'sort-' + $scope.sort.descending;
  };

  $scope.changeSorting = function(column) {
    var sort = $scope.sort;
    if (sort.column == column) {
      sort.descending = !sort.descending;
    }
    else {
      sort.column = column;
      sort.descending = false;
    }
  };

  /* SIGNALS */
  $scope.$on('update-proc', function(e, p) {
    $scope.proc = p;
  });

  $scope.closeApp = function() {
    $scope.emit('close');
  };

  $scope.emit('start-proc-watch');
});
