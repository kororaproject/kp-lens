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

import os
import subprocess

from Lens.LensView import LensView
from Lens.LensThread import LensThread, LensThreadManager

__toolkits = []

# find Gtk
try:
  from LensAppGtk import LensViewGtk
  __toolkits.append('gtk')

except:
  pass

# load Qt
try:
  from LensAppQt import LensViewQt
  __toolkits.append('qt')

except:
  pass


def available_toolkits():
  global __toolkits
  return __toolkits



class LensApp():
  def __init__(self, toolkit=None, toolkit_hint='gtk', name="MyLensApp", width=640, height=480, *args, **kwargs):
    self._app_name = name
    self._app_width = width
    self._app_height = height

    if toolkit is None:
      toolkit = self.__get_desktop_toolkit_hint(toolkit_hint)

    # validate toolkit availability
    if toolkit not in available_toolkits():
      raise Exception('Toolkit %s is not available: %s' % (toolkit, available_toolkits))

    if toolkit == 'gtk':
      self._lv = LensViewGtk(name=name, width=width, height=height)
    elif toolkit == 'qt':
      self._lv = LensViewQt(name=name, width=width, height=height)
    else:
      raise Exception('Toolkit %s is not implemented' % toolkit)



    self.manager = self._lv._manager

  def __get_desktop_toolkit_hint(self, hint):

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

  @property
  def app_name(self):
    return self._app_name

  @app_name.setter
  def app_name(self, name):
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

  def load_app(self, uri):
    uri = 'file://' +  os.path.abspath( uri )

    self._lv.load_uri(uri)

  def on(self, name, callback):
    self._lv.on(name, callback)

  def run(self):
    self._lv._run()

  def set_size(self, width, height):
    self._lv.set_size(width, height)

  def set_title(self, title):
    self._lv.set_title(title)

