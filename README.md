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
from lens.app import App

app = App()

# load the app entry page
app.namespaces.append('./app-data')
app.load_ui('app.html')

@app.connect('close')
def _close_app_cb(*args):
  app.close()

@app.connect('get-hostname')
def _get_hostname_cb(*args):
  app.emit('update-config', os.uname()[1])

app.start()
```

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <link href="lens://css/lens.css" rel="stylesheet">
  <link href="app://css/app.css" rel="stylesheet">
</head>
<body>
  <h1>Lens. Demo</h1>
  <p>This sample demonstrates most of the widgets supported by Lens. Leveraging the Bootstrap and the Angular UI projects, the scope for Lens widgets are limited only by your abilities in HTML5, CSS3 and JS.</p>
  <p>Hostname: <span id="hostname"></span></p>
  <button id="close">CLOSE</button>

  <script src="lens://js/lens-angular.min.js"></script>
  <script src="app://js/app.js"></script>
  <script>

  </script>
</body>
</html>
```

```
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
