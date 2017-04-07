#! /usr/bin/env python3
#
# Copyright 2012-2017 "Korora Project" <dev@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the temms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import platform
from lens.app import App

app = App()

# bind to the 'close' signal
@app.bind('close')
def _close_app_cb(*args):
  app.close()

# bind to the 'get-hostname' signal
@app.bind('get-hostname')
def _get_hostname_cb(*args):
  app.emit('update-hostname', platform.node())

# start the app event loop
app.start("""
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <link href="lens://css/lens.css" rel="stylesheet">
  </head>
  <body>
    <h1>Lens. Demo</h1>
    <p>This sample demonstrates simple communication between the Python and JS code paths.</p>
    <p>Hostname: <span id="hostname"></span></p>
    <div class="text-center">
      <button id="closeBtn">CLOSE</button>
    </div>

    <script src="lens://js/lens.js"></script>
    <script>
      document.addEventListener("DOMContentLoaded", function(event) {
        document.getElementById("closeBtn").onclick = function() {
          lens.emit('close');
        };

        lens.on('update-hostname', function(e, hostname) {
          document.getElementById('hostname').innerHTML = hostname;
        });

        lens.emit('get-hostname');
      });
    </script>
  </body>
  </html>
""")

