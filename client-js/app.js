(function () {
  'use strict';

  angular
    .module('app', ['ngRoute', 'ngCookies', 'ngAnimate', 'ngSanitize', 'ui.bootstrap', 'chart.js'])
    .config(config)
    .run(run);

  config.$inject = ['$routeProvider', '$locationProvider', 'ChartJsProvider'];
  function config($routeProvider, $locationProvider, ChartJsProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: 'home/home.view.html',
        controllerAs: 'vm'
      })

      .when('/login', {
        controller: 'LoginController',
        templateUrl: 'login/login.view.html',
        controllerAs: 'vm'
      })

      .when('/register', {
        controller: 'RegisterController',
        templateUrl: 'register/register.view.html',
        controllerAs: 'vm'
      })

      .when('/playsolo', {
        controller: 'SoloGameController',
        templateUrl: 'sologame/sologame.view.html',
        controllerAs: 'vm'
      })

      .when('/multi', {
        controller: 'MultiController',
        templateUrl: 'multi/multi.view.html',
        controllerAs: 'vm'
      })

      .otherwise({ redirectTo: '/login' });

    // Configure all charts
    ChartJsProvider.setOptions({
      chartColors: ['#ff9800', '#a3a1a1'],
      responsive: true,
      showLines: true,
    });

  }// end conf

  run.$inject = ['$rootScope', '$location', '$cookies', '$http'];
  function run($rootScope, $location, $cookies, $http) {
    $rootScope.backend = "https://api.yaker.drakirus.com"
    $rootScope.backendWs = "wss://ws.yaker.drakirus.com"
    // DEV
    // $rootScope.backend = "http://localhost:8000"
    // $rootScope.backendWs = "ws://localhost:8000"
    // keep user logged in after page refresh
    $rootScope.globals = $cookies.getObject('globals') || {};
    if ($rootScope.globals.currentUser) {
      $http.defaults.headers.common['Authorization'] = 'Token ' + $rootScope.globals.currentUser.token;
    }

    $rootScope.$on('$locationChangeStart', function (event, next, current) {
      // redirect to login page if not logged in and trying to access a restricted page
      var restrictedPage = ['/login', '/register'].indexOf( $location.path() ) === -1;
      var loggedIn = $rootScope.globals.currentUser;
      if (restrictedPage && !loggedIn) {
        $location.path('/login');
      }
    });

  } //end run

})();
