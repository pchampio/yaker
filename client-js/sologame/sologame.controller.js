(function () {
  'use strict';

  angular
    .module('app')
    .controller('SoloGameController', SoloGameController);

  SoloGameController.$inject =
    ['UserService', 'FlashService', '$rootScope',
      '$location',     '$route',    '$uibModal',
      '$document',    '$window',     '$timeout',  '$scope'];

  function SoloGameController(
    UserService, FlashService,
    $rootScope,   $location,   $route,
     $uibModal,   $document,   $window, $timeout, $scope) {

    var vm = this;


    var token  = $rootScope.globals.currentUser.token;
    var svg    = null;
    var socket = null;
    var newGame;

    // init the ctrl
   initCtrl();

    // methods Public
    vm.place = place;
    vm.reload = reload;


    function initCtrl(){

      // method protected
      vm.open = open;

      vm.game = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]];
      vm.lineHeight = 50;

      enableResizeCell();
      newGame = true;

      initSocket();
    }

    function initSocket(){
      socket = new WebSocket($rootScope.backendWs + "/playsolo/?token=" + token);
      socket.onmessage = function(e) {
        var response = JSON.parse(e.data);

        // var response = JSON.parse(`{"score": 24, "board": [[9, 8, 4, 8, 9],
        // [11, 9, 10, 9, 10], [8, 9, 6, 7, 5], [7, 10, 9, 10, 6], [6, 10, 10, 4, 3]],
        // "world_first": [{"name": "drakirus", "score": 31}, {"name": "test", "score": 24}],
        // "followers_best": [{"name": "drakirus", "score": 31,
        // "board": [[6, 10, 7, 9, 9], [9, 6, 10, 7, 8], [10, 9, 9, 10, 4],
        // [6, 10, 8, 5, 8], [3, 4, 11, 10, 9]]}]}`)

        responseGestion(response);

        // event doit trigger dom reload
        $rootScope.$apply();
      }

      // socket init
      socket.onopen = function() {
        socket.send(JSON.stringify({
          i:'init'
        }));
      }
      if (socket.readyState == WebSocket.OPEN) socket.onopen();

      socket.onclose = function (e) {
        if (vm.score) {
          return;
        }
        FlashService.Error('<strong><u>Error:</u> Could not connect to the Api</strong>',false);
        $location.path('/');
      };
    }

    function enableResizeCell(){
      var appWindow = angular.element($window);

      angular.element(document).ready(function () {
        vm.lineHeight = (angular.element(document.querySelector('.cell'))[0].clientWidth);
      });

      appWindow.bind('resize', resize);

      function resize() {
        var oldLineHeight = vm.lineHeight;
        vm.lineHeight = (angular.element(document.querySelector('.cell'))[0].clientWidth);
        if (vm.lineHeight != oldLineHeight)
          $rootScope.$apply()
      }

      $scope.$on('$destroy', function(e) {
        appWindow.unbind('resize', resize);
      });

    }

    function place(i,j){
      socket.send(JSON.stringify({
        i:i, j:j
      }));
    }

    function reload(){
      $route.reload();
    }

    function responseGestion(response){
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
        if (response.error) {
          if (newGame == false){
            svg = angular.element(document.querySelector('#svg'));
            svg.addClass('shake');
            $timeout(function(){
              svg.removeClass('shake');
            }, 500);
          }
          newGame = false;
        }
      }
    }

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
    }; // end modal


    $scope.$on('$locationChangeStart', function( event ) {
      // keep ws clean
      if (socket) {
        socket.close();
      }
    });

  }


})();
