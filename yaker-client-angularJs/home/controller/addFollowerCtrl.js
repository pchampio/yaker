(function () {
  'use strict';
  angular.module('app').controller('addFollowerCtrl',

    function($uibModalInstance, $http, FlashService, UserService, user, notif) {
      var $ctrl = this;
      $ctrl.user = user;
      $ctrl.notif = notif;
      $ctrl.dataLoading = false;
      $ctrl.ErrorLoading = false;


      $ctrl.ok = function() {
        $ctrl.dataLoading = true;
        UserService.AddFollower($ctrl.user)
          .then(function successCallback(response) {
            $ctrl.dataLoading = false;
            FlashService.Success("<strong>" + $ctrl.user + ' is followed</strong>', true);
            $uibModalInstance.close($ctrl.notif);
          }, function errorCallback(response) {
            $ctrl.dataLoading = false;
            $ctrl.ErrorLoading = true;
            $ctrl.msgError= response.data.non_field_errors[0];
          });
      };

      $ctrl.cancel = function() {
        $uibModalInstance.dismiss('cancel');
      };
    });

})();
