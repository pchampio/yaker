(function () {
  'use strict';

  angular
    .module('app')
    .controller('RegisterController', RegisterController);

  RegisterController.$inject = ['UserService', '$location', '$rootScope', 'FlashService'];
  function RegisterController(UserService, $location, $rootScope, FlashService) {
    var vm = this;

    vm.register = register;

    function register() {
      vm.dataLoading = true;
      UserService.Create(vm.user)
        .then(function (response) {
          if (response.success) {
            FlashService.Success('<strong>Registration successful</strong>', true);
            $location.path('/');
          } else {
            vm.error = response.message
            vm.dataLoading = false;
          }
        });
    }
  }

})();
