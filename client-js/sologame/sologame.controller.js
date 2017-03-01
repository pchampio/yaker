(function () {
  'use strict';

  angular
    .module('app')
    .controller('SoloGameController', SoloGameController);

  SoloGameController.$inject = ['$location', 'UserService',
    'FlashService', '$rootScope',
    '$route', '$uibModal', '$document', '$window'];
  function SoloGameController($location, UserService,
    FlashService, $rootScope,
    $route, $uibModal, $document, $window) {
    var vm = this;

    vm.place = place;
    vm.reload = reload;
    vm.game = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]];
    vm.open = open;
    vm.lineHeight = 50;

    var appWindow = angular.element($window);

    angular.element(document).ready(function () {
      vm.lineHeight = ($('.cell').width());
    });

    appWindow.bind('resize', function () {
      vm.lineHeight = ($('.cell').width());
      $rootScope.$apply()
    });


    function place(i,j){
      socket.send(JSON.stringify({
        i:i, j:j
      }));
    }

    function reload(){
      $route.reload();
    }

    var token = $rootScope.globals.currentUser.token;

    var socket = new WebSocket("ws://" + $rootScope.backendWs + "/playsolo/?token=" + token);
    socket.onmessage = function(e) {

      var response = JSON.parse(e.data)

      // var response = JSON.parse(`{"score": 24, "board": [[9, 8, 4, 8, 9],
      // [11, 9, 10, 9, 10], [8, 9, 6, 7, 5], [7, 10, 9, 10, 6], [6, 10, 10, 4, 3]],
      // "world_first": [{"name": "drakirus", "score": 31}, {"name": "test", "score": 24}],
      // "followers_best": [{"name": "drakirus", "score": 31,
      // "board": [[6, 10, 7, 9, 9], [9, 6, 10, 7, 8], [10, 9, 9, 10, 4],
      // [6, 10, 8, 5, 8], [3, 4, 11, 10, 9]]}]}`)

      console.log(response);

      // fin de la game
      if (response.score) {
        vm.dice = null;
        vm.game = response.board;
        vm.score = response.score;
        vm.world_first = response.world_first;
        vm.followers_best = response.followers_best;
      }else{
        // game normale
        vm.game = response.board;
        vm.dice = response.dice;
      }
      // event doit trigger dom reload
      $rootScope.$apply()

    }
    socket.onopen = function() {

      socket.send(JSON.stringify({
        i:'init'
      }));

    }
    // Call onopen directly if socket is already open
    if (socket.readyState == WebSocket.OPEN) socket.onopen();

    function open(size, row, parentSelector){
      var parentElem = parentSelector ?
        angular.element($document[0].querySelector('.modal-demo ' + parentSelector)) : undefined;
      var modalInstance = $uibModal.open({
        animation: true,
        ariaLabelledBy: 'modal-title',
        ariaDescribedBy: 'modal-body',
        templateUrl: 'howFollowerBoard.html',
        controller: 'howFollowerBoard',
        controllerAs: 'vm',
        size: size,
        appendTo: parentElem,
        resolve: {
          row: function() {
            return row;
          }
        }
      });

      modalInstance.result.then(function(rep) {
        console.log(rep);
      }, function() {
        console.log('Modal dismissed at: ' + new Date());
      });
    };

  }


})();
