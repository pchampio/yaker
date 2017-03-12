(function () {
  'use strict';

  angular
    .module('app')
    .factory('UserService', UserService);

  var Base64={keyStr:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",encode:function(e){var r,t,a,h,i,n="",c="",d="",o=0;do r=e.charCodeAt(o++),t=e.charCodeAt(o++),c=e.charCodeAt(o++),a=r>>2,h=(3&r)<<4|t>>4,i=(15&t)<<2|c>>6,d=63&c,isNaN(t)?i=d=64:isNaN(c)&&(d=64),n=n+this.keyStr.charAt(a)+this.keyStr.charAt(h)+this.keyStr.charAt(i)+this.keyStr.charAt(d),r=t=c="",a=h=i=d="";while(o<e.length);return n},decode:function(e){var r,t,a,h,i,n="",c="",d="",o=0,s=/[^A-Za-z0-9\+\/\=]/g;s.exec(e)&&window.alert("There were invalid base64 characters in the input text.\nValid base64 characters are A-Z, a-z, 0-9, '+', '/',and '='\nExpect errors in decoding."),e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");do a=this.keyStr.indexOf(e.charAt(o++)),h=this.keyStr.indexOf(e.charAt(o++)),i=this.keyStr.indexOf(e.charAt(o++)),d=this.keyStr.indexOf(e.charAt(o++)),r=a<<2|h>>4,t=(15&h)<<4|i>>2,c=(3&i)<<6|d,n+=String.fromCharCode(r),64!=i&&(n+=String.fromCharCode(t)),64!=d&&(n+=String.fromCharCode(c)),r=t=c="",a=h=i=d="";while(o<e.length);return n}};
  UserService.$inject = ['$http', '$cookies', '$rootScope'];
  function UserService($http, $cookies, $rootScope) {
    var service = {};

    service.Create = Create;
    service.ClearCredentials = ClearCredentials;
    service.SetCredentials = SetCredentials;
    service.Login = Login;
    service.Logged = Logged;
    service.DeleteNotif = DeleteNotif;
    service.AddFollower = AddFollower;
    service.DelFollower = DelFollower;

    return service;

    function Logged(token){
      return $http.get($rootScope.backend + '/users/me/' )
        .then(dummyCallback, dummyCallback);
    }

    function DeleteNotif(id){
      return $http.delete($rootScope.backend + '/users/me/notif/' + id + '/' )
        .then(dummyCallback, dummyCallback);
    }

    function AddFollower(usernameF){
        var data= { 'follower' : usernameF };
        return $http.post($rootScope.backend + '/users/me/follower/', data);
    }

    function DelFollower(usernameF){
        var data= { 'follower' : usernameF };
        return $http.post($rootScope.backend + '/users/me/follower/delete/', data);
    }


    function Create(user) {
      return $http.post($rootScope.backend + '/users/register/', user)
        .then(
          function successCallback(response) {
            SetCredentials(response);
            return { success: true };
          },
          function errorCallback(response) {
            return { success: false, message: response.data };
          }
        );
    }

    function ClearCredentials(){
      $rootScope.globals = {};
      $cookies.remove('globals');
      $http.defaults.headers.common.Authorization = '';
    }

    function SetCredentials(response){
      // set default auth header for http requests
      $http.defaults.headers.common['Authorization'] = 'Token ' + response.data.token

      $rootScope.globals = {
        currentUser: {
          token: response.data.token,
          user_id: response.data.user_id
        }
      };

      // store user details in globals cookie that keeps user logged in for 1 week (or until they logout)
      var cookieExp = new Date();
      cookieExp.setDate(cookieExp.getDate() + 7);
      $cookies.putObject('globals', $rootScope.globals, { expires: cookieExp });
    }

    function Login(username, password, callback){
      $http.defaults.headers.common.Authorization = 'Basic ' +
        Base64.encode(username + ':' + password);

      $http.get($rootScope.backend + '/users/login/' )
        .then(function successCallback(response) {
          callback(response);
        }, function errorCallback(response) {
          console.log(response.data);
          response = { success: false, message: 'Username or password is incorrect' };
          callback(response);
        });
      // restore old defaults
      $http.defaults.headers.common.Authorization = '';
    }

    // private
    function dummyCallback(res){return res}

  }

})();
