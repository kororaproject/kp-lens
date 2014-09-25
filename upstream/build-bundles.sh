#!/bin/bash

cat lens-data/js/{jquery,angular,angular-route,angular-animate,bootstrap}.js lens-data/js/{lens-bridge,lens-ui}.js > lens-data/js/lens.js
cat lens-data/js/{jquery,angular,angular-route,angular-animate,bootstrap}.min.js lens-data/js/{lens-bridge,lens-ui}.js > lens-data/js/lens.min.js
