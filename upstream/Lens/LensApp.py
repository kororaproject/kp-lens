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

from Lens import LensView



class LensApp():

  def __init__(self, name="MyLensApp", width=640, height=480, *args, **kwargs):
    self._app_name = name
    self._app_width = width
    self._app_height = height

    self._lv = LensView.LensView(name=name, width=width, height=height)

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

