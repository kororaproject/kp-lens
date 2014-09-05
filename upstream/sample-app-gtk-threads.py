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

from Lens.LensAppGtk import LensAppGtk
from Lens.LensThread import LensThread

class LongTaskThread(LensThread):
  def __init__(self):
    LensThread.__init__(self)

  def run(self):
    self.emit('started', self.uuid)
    for i in range(100):
      time.sleep(.05)
      print('progress: %d / 100' % (i))
      self.emit('progress', self.uuid, i)

    self.emit('complete', self.uuid)


app = LensAppGtk()

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
  #app.manager.create(_post_init_finished_cb, _null_cb, None, config.post_init)
  t = LongTaskThread()
  app.manager.add_thread(t)
  app.manager.on_thread(t, 'progress', _longtask_progress_cb)
  app.manager.on_thread(t, 'complete', _longtask_complete_cb)


def _longtask_progress_cb(uuid, progress):
  app.emit('long-task-progress', uuid, progress)

def _longtask_complete_cb(t, *args):
  print(list(args))
  app.emit('long-task-complete', 'Yay! FINISHED!')

app.run()

