# Light ENvironment-agnostic SDK

## Introduction

A lightweight envrionment-agnostic SDK for constructing graphical user interfaces.



## App

A typical Lens app is composed of two phases, there's the backend which is
written in python and the frontend which is composed of HTML5/CSS3/JS similar
to web development.

A bridge exists between the Python and WebKit components that can be traversed
through signal/slot calls. For example Python slots can be reached via WebKit
signals and conversely Webkit slots can be reached via Python signals.

A simple app is shown below.

```python
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
```

## Developing

### Debug

During the development process it's possible to expose internal Lens debugging
by using the `LENS_DEBUG` environment variable. Setting the variable to 1 will
enable verbose Lens debugging messages.

```
LENS_DEBUG=1 ./app
```

### Inspector

On the WebKit side it's possible to get full Inspector ability by using the
`LENS_INSPECTOR` environment variable. Setting the variable to 1 will enable
right-click and opening of the Inspector.

```
LENS_INSPECTOR=1 ./app
```

When using QtWebEngine as the toolkit, setting `LENS_INSPECTOR=1` will start the
remote debugging console on port 8001. The console is accessible using a
chromium based browser. The port can be changed by setting `QTWEBENGINE_REMOTE_DEBUGGING`
to the desired port.
