(function () {
  "use strict";

  angular
    .module('app')
    .directive('regles', regles);

  function regles(){
    return {
      restrict: 'E',
      scope: false,
      templateUrl: '/app-directive/regles.template.html'
    };
  }

})();
