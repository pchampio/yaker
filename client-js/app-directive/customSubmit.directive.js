(function () {
  "use strict";

  angular
    .module('app')
    .directive('customSubmit', customSubmit);

  function customSubmit(){
    return {
      require: '^form',
      scope: {
        fire: '&'
      },
      link: function(scope, element, attrs, form) {
        element.on('click', function(e) {
          scope.$apply(function() {
            form.$submitted = true;
            if (form.$valid) {
              scope.fire()
            }
          });
        });
      }
    };
  }

})();
