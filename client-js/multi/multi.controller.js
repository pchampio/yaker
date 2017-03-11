(function () {
  "use strict";

  angular
    .module('app')
    .controller('MultiController', MultiController);

  MultiController.$inject = ['FlashService', '$rootScope', '$http', '$scope', '$location', '$controller', '$window'];

  MultiController.prototype = Object.create (MultiController.prototype);

  function MultiController(FlashService, $rootScope, $http, $scope, $location, $controller, $window) {

    var vm = this;


    vm.joinLobby = joinLobby;
    vm.createLobby = createLobby;
    vm.userID = $rootScope.userID;
    vm.banUser = banUser;
    vm.startGame = startGame;
    vm.place = place;

    if ($rootScope.userID == null) {
      $location.path('/');
    }

    var token = $rootScope.globals.currentUser.token;
    var socket = null;

    vm.lineHeight = 50;
    vm.gamestart = false;

    function createLobby() {
      vm.dataLoading = true;
      $http.get($rootScope.backend + "/game/lobby/available/", {params:{"room": vm.lobbyName}})
        .then(
          function successCallback(response) {
            vm.dataLoading = false;
            vm.lobbyError = false;
            joinLobby()
          },
          function errorCallback(response) {
            vm.dataLoading = false;
            vm.lobbyError = true;
          }
        );
    }

    vm.nbBoardSeen = 0; // do not display first error when game start up
    vm.dice = null;
    function joinLobby() {

      socket = new WebSocket($rootScope.backendWs + "/playmulti/lobby/?token=" + token + "&room=" + vm.lobbyName);

      socket.onmessage = function(e) {

        var response = JSON.parse(e.data.replace(/'/g, '"'));
        var response = JSON.parse(e.data);

        FlashService.Clear()
        vm.dataLoading = true;

        if (angular.equals(vm.lobbyInfo, response)) {
          // more js compute less dom YAY
          return;
        }

        if (response.ingame && vm.gamestart == false) {
          vm.nbBoardSeen = 1
          socket.send(JSON.stringify({
            ini :1
          }));
          vm.gamestart = true;

        }

        if (response.error && vm.nbBoardSeen != 1) {
          FlashService.Error('<strong><u>Error:</u> '+ response.error + '</strong>',false);
          if (vm.gamestart == false) {
            resetLobby();
            return;
          }
        }

        if(response.ban && response.ban.indexOf(vm.userID) !== -1){
          FlashService.Error('<strong><u>Error:</u> You are banned from lobby ' + vm.lobbyName +'</strong>',false);
          resetLobby();
          return;
        }

        if (response.op) {
          vm.lobbyInfo = response;
        }
        if (response.dice) {
          vm.dice = response.dice;
        }
        if (response.score && response.user_id == vm.userID) {
          vm.score = response.score;
        }
        if (response.score) {
          for (var i = 0; i < vm.lobbyInfo.players.length; i++) {
            if (response.user_id == vm.lobbyInfo.players[i]["id"]) {
              vm.lobbyInfo.players[i].score = response.score;
            }
          }
        }
        if (response.board){
          vm.nbBoardSeen = 2;
          vm.game = response.board;
          enableResizeCell();
        }

        $rootScope.$apply()
      }

      // Call onopen directly if socket is already open
      if (socket.readyState == WebSocket.OPEN){
        vm.dataLoading = false;
        socket.onopen();
      }

      socket.onclose = function (e) {
        vm.lobbyInfo = null;
        vm.dataLoading = false;
        $scope.$apply()
      };
    }

    function banUser(userID){
      socket.send(JSON.stringify({
        ban: userID,
      }));
    }

    function startGame(){
      socket.send(JSON.stringify({
        startGame: 1,
      }));
    }

    function place(i,j){
      socket.send(JSON.stringify({
        i:i, j:j
      }));
    }

    // Private

    $scope.$on('$locationChangeStart', function( event ) {
      // keep ws clean
      if (socket) {
        socket.close();
      }
    });

    function resetLobby(){
      if (socket) {
        socket.close();
      }
      vm.lobbyInfo = null;
      vm.game = null;
      vm.dice = null;
      $scope.$apply()
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

  }// end ctrl

})();
