#!/bin/bash
uglifyjs dist/angular.min.js dist/angular-route.min.js dist/angular-cookies.min.js dist/angular-animate.min.js dist/angular-sanitize.min.js dist/ui_bootstrap_tpls_2.5.0.min.js dist/Chart.min.js dist/angular-chart.min.js app.js app-services/*.js app-directive/customSubmit.directive.js app-directive/regles.directive.js home/home.controller.js login/login.controller.js register/register.controller.js sologame/sologame.controller.js multi/multi.controller.js sologame/controller/howFollowerBoard.js home/controller/addFollowerCtrl.js -o yaker.min.js
