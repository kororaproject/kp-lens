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

import os
import pprint
import time

from lens.app import App
from lens.thread import Thread

class ProcTask(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while 1:
            pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

            loadavg = open('/proc/loadavg', 'r').read().strip().split(' ')
            meminfo = [x.split()[1] for x in open('/proc/meminfo', 'r').read().strip().split('\n')]

            proc = []

            for pid in pids:
                try:
                    stats = open(os.path.join('/proc', pid, 'stat'), 'r').read().strip().split(' ')
                    statm = open(os.path.join('/proc', pid, 'statm'), 'r').read().strip().split(' ')
                    cmdline = open(os.path.join('/proc', pid, 'cmdline'), 'r').read()

                    proc.append({
                        'cmdline': cmdline,
                        'pid': int(stats[0]),
                        'comm': stats[1],
                        'state': stats[2],
                        'ppid': int(stats[3]),
                        'priority': int(stats[17]),
                        'nice': int(stats[18]),
                        'vsize': int(stats[22]),
                        'mem_size': int(statm[0]),
                        'mem_resident': int(statm[1]),
                        'mem_shared': int(statm[2]),
                        'mem_percentage': round(int(statm[1]) * 100.0 / int(meminfo[0]), 2)
                    })

                except:
                    # proc has already terminated
                    continue

            self.emit('proc-update', proc)

            time.sleep(5)


app = App(inspector=True, name='LensTop')

# load the app entry page
app.namespaces.append('./sample-data/app-top')

@app.bind('close')
def _close_app_cb(*args):
    app.close()

@app.bind('start-proc-watch')
def _start_proc_watch_cb(*args):
    t = ProcTask()
    t.daemon = True
    app.threads.add(t)
    app.threads.on(t, 'proc-update', _proctask_update_cb)

def _proctask_update_cb(thread, proc):
    app.emit('update-proc', proc)

app.start()
