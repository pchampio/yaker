(function () {
  'use strict';

  angular
    .module('app')
    .controller('LoginController', LoginController);

  LoginController.$inject = ['$location', 'UserService', 'FlashService'];
  function LoginController($location, UserService, FlashService) {
    var vm = this;

    vm.login = login;

    // reset login status
    UserService.ClearCredentials();

    function login() {
      vm.dataLoading = true;
      UserService.Login(vm.username, vm.password, function (response) {
        if (response.status === 200) {
          UserService.SetCredentials(response);
          $location.path('/');
        } else {
          FlashService.Error(response.message);
          vm.dataLoading = false;
        }
      });
    };
  }

})();
