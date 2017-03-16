(function () {
  "use strict";

  angular
    .module('app')
    .controller('HomeController', HomeController);

  HomeController.$inject = ['UserService', 'FlashService', '$rootScope', '$uibModal', '$document', '$scope'];
  function HomeController(UserService, FlashService, $rootScope, $uibModal, $document, $scope) {
    var vm = this;

    vm.notif = [];
    vm.user = $rootScope.globals.currentUser.username;

    vm.deleteNotif  = deleteNotif;
    vm.open         = open;
    vm.addFollower  = addFollower;
    vm.dellFollower = dellFollower;


    initController();

    function initController() {
      $scope.labels = ["", "", "", "", "", "", ""];
      $scope.data = [
        [0, 0, 0, 0, 0, 0, 0]
      ];

      loadCurrentUser();
    }

    function loadCurrentUser() {
      UserService.Logged()
        .then(function (res) {
          vm.notif = res.data.notif;
          $rootScope.globals.currentUser.user_id = res.data.user_id; // just in case
          vm.first = res.data.best_last[0];
          vm.sec = res.data.best_last[1];
          vm.th = res.data.best_last[2];
          vm.avg =  res.data.score__avg;
          vm.worst =  res.data.worst;
          for (var i = 0, len = res.data.last_games.length; i < len; i++) {
            $scope.labels[i] = res.data.last_games[i].date;
            $scope.data[0][i] = (res.data.last_games[i].score);
          }
          if (!vm.notif) {
            return;
          }
          for (var i = 0; i < vm.notif.length; i++) {
            if (vm.notif[i].type == 'Follower'){
              vm.notif[i]["class"] = "info"
            }
            else if (vm.notif[i].type == 'Info'){
              vm.notif[i]["class"] = "success"
            }
          }
        });
    }

    function deleteNotif(id) {
      UserService.DeleteNotif(id);
      for (var i = 0; i < vm.notif.length; i++) {
        if (vm.notif[i].id_cache == id) {
          vm.notif.splice(i,1);
          return;
        }
      }
    }

    function addFollower(){
      vm.dataLoading = true;
      UserService.AddFollower(vm.follower)
        .then(function successCallback(response) {
          vm.dataLoading = false;
          FlashService.Success("<strong><u>" + vm.follower + '</u> is followed</strong>',false);
        }, function errorCallback(response) {
          vm.dataLoading = false;
          FlashService.Error("<strong>" + response.data.non_field_errors[0] + '</strong>', false);
        });
    }

    function dellFollower(){
      vm.dataLoading = true;
      UserService.DelFollower(vm.follower)
        .then(function successCallback(response) {
          vm.dataLoading = false;
          FlashService.Success("<strong><u>" + vm.follower + '</u> is unfollowed</strong>', false);
        }, function errorCallback(response) {
          vm.dataLoading = false;
          FlashService.Error("<strong>" + response.data.detail + '</strong>', false);
        });
    }

    function open(size, notif, parentSelector){
      var parentElem = parentSelector ?
        angular.element($document[0].querySelector('.modal-demo ' + parentSelector)) : undefined;
      var modalInstance = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'modal-title',
        ariaDescribedBy: 'modal-body',
        templateUrl: 'addFollowerModal.html',
        controller: 'addFollowerCtrl',
        controllerAs: 'vm',
        size: size,
        appendTo: parentElem,
        resolve: {
          user: function() {
            return notif.related[0];
          },
          notif: function() {
            return notif.id_cache;
          }
        }
      });

      modalInstance.result.then(function(notif) {
        deleteNotif(notif)
      }, function() {
        console.log('Modal dismissed at: ' + new Date());
      });
    };

  }

})();
