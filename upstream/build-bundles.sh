#!/bin/bash

# lens core
cat lens-data/js/{jquery,lens-core}.js > lens-data/js/lens.js
cat lens-data/js/{jquery,lens-core}.min.js > lens-data/js/lens.min.js

# lens angular + core
cat lens-data/js/{jquery,angular,angular-route,angular-animate,bootstrap}.js lens-data/js/{lens-core,lens-bridge,lens-ui}.js > lens-data/js/lens-angular.js
cat lens-data/js/{jquery,angular,angular-route,angular-animate,bootstrap}.min.js lens-data/js/{lens-core,lens-bridge,lens-ui}.js > lens-data/js/lens-angular.min.js
