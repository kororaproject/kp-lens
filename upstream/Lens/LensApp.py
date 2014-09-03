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

import inspect
import os
import pprint
import signal
import subprocess
import sys
import threading

from Lens import LensView, LensViewGTK

# GTK
from gi.repository import WebKit2, Gtk, GObject

class _GIdleObject(GObject.GObject):
  '''
  Override gobject.GObject to always emit signals in the main thread
  by emmitting on an idle handler
  '''
  def __init__(self):
    GObject.GObject.__init__(self)

  def emit(self, *args):
    GObject.idle_add(GObject.GObject.emit, self, *args)

class _GThread(threading.Thread, _GIdleObject):
  '''
  Thread which uses GObject signals to return information
  to the GUI.
  '''
  __gsignals__ = {
    "completed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    "progress":  (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))
  }

  def __init__(self, target=None, args=(), kwargs={}):
    threading.Thread.__init__(self, target=target, *args, **kwargs)
    _GIdleObject.__init__(self)

    self.daemon = True

  def run(self):
    threading.Thread.run(self)

    self.emit("completed")

class ThreadManager():
  '''
  Manages many _GThreads. This involves starting and stopping
  said threads, and respecting a maximum num of concurrent threads limit
  '''
  def __init__(self, maxConcurrentThreads):
    self.maxConcurrentThreads = maxConcurrentThreads

    #stores all threads, running or stopped
    self.threads = {}

    #the pending thread args are used as an index for the stopped threads
    self.pendingThreadArgs = []

  def _register_thread_completed(self, thread, *args):
    '''
    Decrements the count of concurrent threads and starts any
    pending threads if there is space
    '''
    del(self.threads[args])
    running = len(self.threads) - len(self.pendingThreadArgs)

    print("%s completed. %s running, %s pending" % (thread, running, len(self.pendingThreadArgs)))

    if running < self.maxConcurrentThreads:
      try:
        args = self.pendingThreadArgs.pop()
        print("Starting pending %s" % self.threads[args])
        self.threads[args].start()
      except IndexError: pass

  def create(self, completedCb, progressCb, userData, target, *args, **kwargs):
    '''
    Makes a thread with args. The thread will be started when there is
    a free slot
    '''
    running = len(self.threads) - len(self.pendingThreadArgs)

    if args not in self.threads:
      thread = _GThread(target=target, *args, **kwargs)

      #signals run in the order connected. Connect the user completed
      #callback first incase they wish to do something
      #before we delete the thread
      thread.connect("completed", completedCb, userData)
      thread.connect("completed", self._register_thread_completed, *args)
      thread.connect("progress", progressCb, userData)

      #This is why we use args, not kwargs, because args are hashable
      self.threads[args] = thread

      if running < self.maxConcurrentThreads:
        print("Starting %s" % thread)
        self.threads[args].start()

      else:
        print("Queing %s" % thread)
        self.pendingThreadArgs.append(args)

  def stop_all(self, block=False):
    '''
    Stops all threads. If block is True then actually wait for the thread
    to finish (may block the UI)
    '''
    for thread in self.threads.values():
      thread.cancel()
      if block:
        if thread.isAlive():
          thread.join()




class LensApp():
  def __init__(self, *args, **kwargs):
    self._app_name = "App"

    # TODO: remove dependency on GTK
    self._lv = LensViewGTK.LensViewGTK()

  def load_app(self, uri):
    uri = 'file://' +  os.path.abspath( uri )

    self._lv.loadURI(uri)

  def close(self):
    self._lv.close()

  def emit(self, name, message):
    self._lv.emitJS(name, message)

  def on(self, name, callback):
    self._lv.on(name, callback)

  def run(self):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()

