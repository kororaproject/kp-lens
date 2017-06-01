#!/usr/bin/python3
#
# Copyright 2012-2017 "Korora Project" <dev@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the temms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import platform
import pprint
import random
import time

from lens.app import App
from lens.thread import Thread

class LongTask(Thread):
  def __init__(self):
    Thread.__init__(self, daemon=True)

  def run(self):
    delta = random.uniform(0.05, 0.5)

    self.emit('started', self.uuid, time.time())

    for i in range(100):
      time.sleep(delta)
      self.emit('progress', self.uuid, i)

    self.emit('complete', self.uuid, time.time())

def _longtask_progress_cb(thread, *args):
  app.emit('long-task-progress', *args)

def _longtask_complete_cb(thread, *args):
  app.emit('long-task-complete', *args)


if __name__ == '__main__':
  app = App(name="Lens. Threads")

  # load the app entry page
  app.namespaces.append('./sample-data/app-threads')

  @app.bind('close')
  def _close_app_cb(*args):
    app.close()

  @app.bind('get-hostname')
  def _get_hostname_cb(*args):
    app.emit('update-config', platform.node())

  @app.bind('update-hostname')
  def _update_hostname_cb(message):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(message)

  @app.bind('start-long-task')
  def _long_task_cb():
    t = LongTask()
    app.threads.add(t)
    app.threads.on(t, 'progress', _longtask_progress_cb)
    app.threads.on(t, 'complete', _longtask_complete_cb)



  app.start()

