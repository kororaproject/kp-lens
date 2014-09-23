#
# Copyright 2012-2014 "Korora Project" <dev@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the temms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import os
import subprocess
import traceback

from Lens.View import View
from Lens.Thread import Thread, ThreadManager

#: defines the list of Lens backends to be preloaded for auto-detection
__preload = {
  'gtk':  ['Lens.AppGtk',  'ViewGtk' ],
  'gtk2': ['Lens.AppGtk2', 'ViewGtk2'],
  'qt':   ['Lens.AppQt',   'ViewQt'  ]
}

__toolkits = {}

#: preload our toolkits and store class object to allow building
for k in __preload:
  try:
    __tk = __preload[k]
    __module = __import__(__tk[0], globals(), locals(), [__tk[1]], 0)
    __toolkits[k] = getattr(__module, __tk[1], None)

  except:
    #traceback.print_exc()
    pass

def get_toolkit(name, exact=False):
  global __toolkits

  if name in __toolkits:
    return __toolkits[name]

  elif exact:
    raise Exception('Toolkit %s is not implemented or could not be loaded.' % name)

  toolkits = __toolkits.keys()
  if len(toolkits):
    fallback = toolkits.pop()
    return __toolkits[fallback]

  raise Exception('No fallback toolkits implemented or loaded.')



class App():
  """The app object implements a Lens application and acts as the central
  object. Once created it will act as a central registry for the view
  toolkit abstraction, thread management, signal handling and much more.

  :param toolkit: force the toolkit to use. If set to `None` the toolkit
                  will be auto detected.
  :param toolkit_hint: hint to the preferred toolkit if the auto detection
                       fails to determine the active toolkit.
  :param name: the name of the Lens application. Also shown in the Lens
               application window's title bar.
  :param width: the width of the Lens applciation window. Defaults to 640.
  :param height the height of the Lens applciation window. Defaults to 480.
  """
  def __init__(self, toolkit=None, toolkit_hint='gtk', name="MyLensApp", width=640, height=480, inspector=False, *args, **kwargs):
    self._logger = logging.getLogger('Lens.App')

    self._app_name = name
    self._app_width = width
    self._app_height = height

    #: determine the toolkit to use and build the appropiate LensView
    if toolkit is None:
      toolkit = self.__get_desktop_toolkit_hint(toolkit_hint.lower())

    toolkit_klass = get_toolkit(toolkit.lower())
    self._lv = toolkit_klass(name=name, width=width, height=height, inspector=inspector)

    #: find lens data path
    base = None
    for d in ["/usr/share/lens", "lens", "lens-data"]:
      if os.path.exists(d):
        if d.startswith('/'):
          base = d
        else:
          base = os.path.join(os.getcwd(), d)
        break

    if base is None:
      raise Exception('Unable to locate lens base data for UI components.')

    self._lv._uri_lens_base = 'file://' + base + '/'

    self._logger.debug("Using lens data path: %s" % self._lv._uri_lens_base)

    #: store an app pointer to the thread manager
    self.manager = self._lv._manager

  def __get_desktop_toolkit_hint(self, hint):
    def __is_running(self, process):
      try:
        # Linux/Unix
        s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
      except:
        # Windows
        s.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)

      for x in s.stdout:
        if re.search(process, x):
          return True

      return False

    toolkit = hint

    if os.environ.get('KDE_FULL_SESSION') == 'true':
      toolkit = 'qt'

    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
      toolkit = 'gtk'

    elif __is_running("xfce-mcs-manage"):
      toolkit = "gtk2"

    elif __is_running("ksmserver"):
      toolkit = 'qt'

    return toolkit

  @property
  def name(self):
    return self._app_name

  @name.setter
  def name(self, name):
    self._app_name = name

    # update window title on app name change
    self._lv.set_title(self._app_name)

  def close(self):
    self._lv.close()

  def connect(self, name):
    """A decorator that is used to register a callback for
       a given signal. Example usage::

         @app.connect('hello')
         def hello_cb():
           print("Hi!")

    :param name: the name of the signal to subscribe to
    """
    def decorator(f):
      self.on(name, f)
      return f

    return decorator

  def emit(self, name, *args):
    self._lv.emit_js(name, *args)

  def load_ui(self, uri):
    """Load the UI from the specified URI.

    :param uri: the uri to the entry page of the UI.
    """
    uri = 'file://' +  os.path.abspath( uri )

    self._lv.load_uri(uri)

  def on(self, name, callback):
    self._lv.on(name, callback)

  def resize(self, width, height):
    """Resizes the application window.

    :param width: the requested width for the application window. If set to
                  `None`, the width won't be changed.
    :param height: the requested height for the application window. If set to
                  `None`, the height won't be changed.
    """
    if width is not None:
      self._app_width = width

    if height is not None:
      self._app_height = height

    self._lv.set_size(self._app_width, self._app_height)

  def set_title(self, title):
    self._lv.set_title(title)

  def start(self):
    self._lv._run()

