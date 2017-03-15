(function () {
  'use strict';
  angular.module('app').controller('howFollowerBoard',

    function($uibModalInstance, $http, FlashService, UserService, row, $rootScope, $window) {
      var $ctrl  = this;
      $ctrl.row  = row;
      $ctrl.game = row.board;

      $ctrl.ok = function() {
        console.log("ok");
        console.log($ctrl.row);
      };


      angular.element(document).ready(function () {
        $ctrl.lineHeight = (angular.element(document.querySelector('.cell'))[0].clientWidth);
      });

      $ctrl.cancel = function() {
        $uibModalInstance.dismiss('cancel');
      };
    });

})();
