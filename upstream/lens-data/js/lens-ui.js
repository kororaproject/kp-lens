angular.module('lens-ui', [])
  .directive('radio', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ngModel: '=',
        value: '@'
      },
      transclude: true,
      template: function (elem, attrs) {
        var classes = attrs.class ? ' ' + attrs.class : '';
        var true_class = attrs.true ? attrs.true : 'fa-dot-circle-o';
        var false_class = attrs.false ? attrs.false : 'fa-circle-o';

        return '<div class="lens-radio' + classes + '">' +
                 '<div ng-click="toggle()">' +
                   '<i class="lens-radio-icon fa fa-fw" ng-class="{\'' + true_class + '\': selected(), \'' + false_class + '\': !selected()}"></i>' +
                   '<div class="lens-radio-label" ng-transclude></div>' +
                 '</div>' +
               '</div>';
      },
      link: function (scope, elem, attrs) {
        scope.toggle = function() {
          scope.ngModel = scope.value;
        }

        scope.selected = function() {
          return scope.ngModel === scope.value;
        }
      }
    }
  })
  .directive('checkbox', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: {
        ngModel: '='
      },
      transclude: true,
      template: function (elem, attrs) {
        var classes = attrs.class ? ' ' + attrs.class : '';
        var true_class = attrs.true ? attrs.true : 'fa-check-square-o';
        var false_class = attrs.false ? attrs.false : 'fa-square-o';

        return '<div class="lens-checkbox"' + classes + '>' +
                 '<div ng-click="toggle()">' +
                   '<i class="lens-checkbox-icon fa fa-fw" ng-class="{\'' + true_class + '\': ngModel, \'' + false_class + '\': !ngModel}"></i>' +
                   '<div class="lens-checkbox-label" ng-transclude></div>' +
                 '</div>' +
               '</div>';
      },
      link: function (scope, elem, attrs) {
        scope.toggle = function() {
          scope.ngModel = !scope.ngModel;
        }
      }
    }
  });
