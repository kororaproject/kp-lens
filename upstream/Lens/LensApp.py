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


  def __init__(self, *args, **kwargs):
    self._app_name = "App"

    self._lv = LensView.LensView()

  def close(self):
    self._lv.close()

  def emit(self, name, message):
    self._lv.emit_js(name, message)

  def load_app(self, uri):
    uri = 'file://' +  os.path.abspath( uri )

    self._lv.load_uri(uri)

  def on(self, name, callback):
    self._lv.on(name, callback)

  def run(self):
    self._lv._run()

  def set_title(self, title):
    self._lv.set_title(title)

  def set_size(self, width, height):
    self._lv.set_size(1024, 768)
