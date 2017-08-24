#!/bin/bash

echo "Updating AngularJS ..."
wget https://code.angularjs.org/1.6.4/angular.js -O ./lens-data/js/angular.js
wget https://code.angularjs.org/1.6.4/angular.min.js -O ./lens-data/js/angular.min.js
wget https://code.angularjs.org/1.6.4/angular.min.js.map -O ./lens-data/js/angular.min.js.map

wget https://code.angularjs.org/1.6.4/angular-animate.js -O ./lens-data/js/angular-animate.js
wget https://code.angularjs.org/1.6.4/angular-animate.min.js -O ./lens-data/js/angular-animate.min.js
wget https://code.angularjs.org/1.6.4/angular-animate.min.js.map -O ./lens-data/js/angular-animate.min.js.map

wget https://code.angularjs.org/1.6.4/angular-route.js -O ./lens-data/js/angular-route.js
wget https://code.angularjs.org/1.6.4/angular-route.min.js -O ./lens-data/js/angular-route.min.js
wget https://code.angularjs.org/1.6.4/angular-route.min.js.map -O ./lens-data/js/angular-route.min.js.map


#echo "Updating JQuery ..."
