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

class ProcTask(Thread):
  def __init__(self):
    Thread.__init__(self)

  def run(self):
    while 1:
      pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

      proc = {}

      for pid in pids:
        try:
          proc[pid] = {
            'cmdline': open(os.path.join('/proc', pid, 'cmdline'), 'rb').read(),
            'stats':   open(os.path.join('/proc', pid, 'stat'), 'rb').read().strip().split(' ')
          }

        except:
          # proc has already terminated
          continue

      self.emit('proc-update', proc)

      time.sleep(3)


app = App(debug_javascript=True)

# load the app entry page
app.load_ui('./sample-data/app-top.html')

@app.connect('close')
def _close_app_cb(*args):
  app.close()

@app.connect('start-proc-watch')
def _start_proc_watch_cb(*args):
  t = ProcTask()
  t.daemon = True
  app.manager.add_thread(t)
  app.manager.on_thread(t, 'proc-update', _proctask_update_cb)

def _proctask_update_cb(thread, proc):
  app.emit('update-proc', proc)

app.start()
