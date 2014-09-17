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

import os
import pprint
import time

from Lens.App import App
from Lens.Thread import Thread

class LongTaskThread(Thread):
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    self.emit('started', self.uuid)

    for i in range(100):
      time.sleep(.05)
      self.emit('progress', self.uuid, i)

    self.emit('complete', self.uuid, 'YAY')


app = App()

# load the app entry page
app.load_app('./sample-data/app-threads.html')

@app.connect('close')
def _close_app_cb(*args):
  app.close()

@app.connect('get-hostname')
def _get_hostname_cb(*args):
  app.emit('update-config', os.uname()[1])

@app.connect('update-hostname')
def _update_hostname_cb(message):
  pp = pprint.PrettyPrinter(indent=2)
  pp.pprint(message)

@app.connect('start-long-task')
def _long_task_cb():
  t = LongTaskThread()
  app.manager.add_thread(t)
  app.manager.on_thread(t, 'progress', _longtask_progress_cb)
  app.manager.on_thread(t, 'complete', _longtask_complete_cb)


def _longtask_progress_cb(thread, *args):
  app.emit('long-task-progress', *args)

def _longtask_complete_cb(thread, *args):
  app.emit('long-task-complete', *args)

app.run()

