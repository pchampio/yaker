(function () {
  "use strict";

  angular
    .module('app')
    .controller('MultiController', MultiController);

  MultiController.$inject =
    ['FlashService', '$rootScope',   '$http',    '$scope',
      '$location',   '$controller', '$window', '$timeout', '$route'];

  MultiController.prototype = Object.create (MultiController.prototype);

  function MultiController(
    FlashService, $rootScope, $http, $scope,
     $location,   $controller, $window , $timeout, $route
  ) {

    var vm = this;


    vm.joinLobby   = joinLobby;
    vm.createLobby = createLobby;
    vm.banUser     = banUser;
    vm.startGame   = startGame;
    vm.place       = place;
    vm.isAdmin     = null;
    vm.userID      = $rootScope.globals.currentUser.user_id;


    if (!vm.userID) {
      FlashService.Error("Client error could not found your user.id",true);
      $location.path('/');
    }

    var token  = $rootScope.globals.currentUser.token;
    var socket = null;

    vm.lineHeight = 50;
    vm.gamestart  = false;

    function createLobby() {
      vm.dataLoading = true;
      $http.get($rootScope.backend + "/game/lobby/available/", {params:{"room": vm.lobbyName}})
        .then(
          function successCallback(response) {
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
    var gameEnd = false;
    function joinLobby() {
      vm.dataLoading = true;

      socket = new WebSocket($rootScope.backendWs + "/playmulti/lobby/?token=" + token + "&room=" + vm.lobbyName);

      socket.onmessage = function(e) {

        vm.dataLoading = false;
        var response = JSON.parse(e.data);
        FlashService.Clear()

        if (angular.equals(vm.lobbyInfo, response) || gameEnd == true) {
          // more js compute less dom YAY
          return;
        }

        // Init game
        if (response.ingame && vm.gamestart == false) {
          vm.nbBoardSeen = 1
          socket.send(JSON.stringify({
            ini :1
          }));
          vm.gamestart = true;

          vm.game =  [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]];

          $timeout(enableResizeCell(), 500); // need timeout ;/
        }

        // on error
        if (response.error && vm.nbBoardSeen != 1) {
          FlashService.Error('<strong><u>Error:</u> '+ response.error + '</strong>',false);
          $window.scrollTo(0, 0);
          if (vm.gamestart == false) {
            resetLobby();
            return;
          }
        }

        // on error (user ban)
        if(response.ban && response.ban.indexOf(vm.userID) !== -1){
          FlashService.Error('<strong><u>Error:</u> You are banned from lobby ' + vm.lobbyName +'</strong>',false);
          resetLobby();
          return;
        }


        // new dice
        if (response.dice) {
          vm.dice = response.dice;
        }

        // info sur les users
        if (response.op) {
          vm.lobbyInfo = response;
          vm.isAdmin = vm.lobbyInfo && vm.lobbyInfo.op === vm.userID;

          for (var i = 0; i < vm.lobbyInfo.players.length; i++) {
            if (vm.userID == vm.lobbyInfo.players[i]["id"]) {
              if (vm.lobbyInfo.players[i].played == 1) {
                vm.dice = "?";
              }
              break;
            }
          }

        }

        // board
        if (response.board){
          vm.nbBoardSeen = 2;
          vm.game = response.board;
        }

        // score of current user
        if (response.score && response.user_id == vm.userID) {
          vm.score = response.score;
        }

        // socre all users
        if (response.score) {
          var nb_players_end = 0;

          for (var i = 0; i < vm.lobbyInfo.players.length; i++) {
            if (response.user_id == vm.lobbyInfo.players[i]["id"]) {
              vm.lobbyInfo.players[i].score = response.score;
            }
            if (vm.lobbyInfo.players[i].score) {
              nb_players_end += 1;
              vm.lobbyInfo.players[i].played = 1; // change status to none
            }
          }

          // End game
          if (nb_players_end >= vm.lobbyInfo.players.length) {
            gameEnd = true;
            $window.scrollTo(0, 0);
          }
        }

        $rootScope.$apply()
      }

      // Call onopen directly if socket is already open
      if (socket.readyState == WebSocket.OPEN){
        socket.onopen();
      }

      socket.onclose = function (e) {
        if (gameEnd) {
          return;
        }
        resetLobby();
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
      $route.reload();
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
