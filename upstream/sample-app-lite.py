#! /usr/bin/env python3

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
    <button id="closeBtn">CLOSE</button>

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

