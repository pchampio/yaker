﻿(function () {
  'use strict';


  $.getScript("home/controller/addFollowerCtrl.js");
  angular
    .module('app')
    .controller('HomeController', HomeController)
    .directive('customSubmit', customSubmit);

  HomeController.$inject = ['UserService', 'FlashService', '$rootScope', '$uibModal', '$document'];
  function HomeController(UserService, FlashService, $rootScope, $uibModal, $document) {
    var vm = this;

    vm.user = null;
    vm.notif = [];

    vm.deleteNotif = deleteNotif;
    vm.open = open;
    vm.addFollower = addFollower;
    vm.dellFollower = dellFollower;

    initController();

    function initController() {
      loadCurrentUser();
    }

    function loadCurrentUser() {
      UserService.Logged()
        .then(function (res) {
          vm.user = res.data.username;
          vm.notif = res.data.notif;
          for (var i = 0; i < vm.notif.length; i++) {
            if (vm.notif[i].type == 'Follower'){
              vm.notif[i]["class"] = 'panel panel-primary';
            }
            else if (vm.notif[i].type == 'Info'){
              vm.notif[i]["class"] = 'panel panel-info';
            }
            else{
              vm.notif[i]["class"] = 'panel panel-warning';
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
