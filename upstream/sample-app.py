#!/usr/bin/python2
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
import pprint

from Lens.App import App

class MyApp(App):
  def __init__(self):
    App.__init__(self, name="SampleApp")

    # load the app entry page
    self.load_app('./sample-data/app.html')

    self.on('close', self._close_app_cb)
    self.on('get-hostname', self._get_hostname_cb)
    self.on('update-hostname', self._update_hostname_cb)

  def _close_app_cb(self, *args):
    self.close()

  def _get_hostname_cb(self, *args):
    self.emit('update-config', os.uname()[1])

  def _update_hostname_cb(self, message):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(message)

logging.basicConfig(level=logging.DEBUG)

app = MyApp()
app.run()

