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

import threading
import time

from Lens.LensView import EventEmitter

class LensThread(EventEmitter):


  def __init__(self):
    EventEmitter.__init__(self)

    # the ID won't change when the name changes
    self._uuid = 'LensThread' + str(time.monotonic())

  @property
  def uuid(self):
    return self._uuid


  def run(self):
    pass


class LensThreadManager(EventEmitter):
  """
  Manages many LensThreads. This involves starting and stopping
  said threads, and respecting a maximum num of concurrent threads limit
  """
  def __init__(self, maxConcurrentThreads=5):
    EventEmitter.__init__(self)

    self.maxConcurrentThreads = maxConcurrentThreads

    #stores all threads, running or stopped
    self.threads = {}

    #the pending thread args are used as an index for the stopped threads
    self.pendingThreadArgs = []

  def _create_thread(self, complete_cb, progress_cb, target=None, *args, **kwargs):
    return LensThread(target=target, *args, **kwargs)

  def _thread_completed_cb(self, thread, *args):
    """
    Decrements the count of concurrent threads and starts any
    pending threads if there is space
    """
    del(self.threads[thread.uuid])
    running = len(self.threads) - len(self.pendingThreadArgs)

    print("%s completed. %s running, %s pending" % (thread, running, len(self.pendingThreadArgs)))

    if running < self.maxConcurrentThreads:
      try:
        uuid = self.pendingThreadArgs.pop()
        print("Starting pending %s" % self.threads[uuid])
        self.threads[uuid].start()
      except IndexError:
        pass

  def _register_thread_signals(self, thread, *args):
    pass

  def add_thread(self, thread):
    # TODO: be nicer
    if not isinstance(thread, LensThread):
      raise TypeError("not a LensThread stupdiD!")

    running = len(self.threads) - len(self.pendingThreadArgs)

    _thread = self._add_thread(thread)
    uuid = _thread.uuid

    if uuid not in self.threads:
      self.threads[uuid] = _thread

      self._register_thread_signals(_thread)

      if running < self.maxConcurrentThreads:
        print("Starting %s" % _thread)
        self.threads[uuid].start()

      else:
        print("Queing %s" % thread)
        self.pendingThreadArgs.append(uuid)

  def create(self, completed_cb, progress_cb, user_data, target, *args, **kwargs):
    """
    Makes a thread with args. The thread will be started when there is
    a free slot
    """
    running = len(self.threads) - len(self.pendingThreadArgs)

    if args not in self.threads:
      thread = self._create_thread(completed_cb, progress_cb, user_data, target=target, *args, **kwargs)

      #This is why we use args, not kwargs, because args are hashable
      self.threads[args] = thread

      if running < self.maxConcurrentThreads:
        print("Starting %s" % thread)
        self.threads[args].start()

      else:
        print("Queing %s" % thread)
        self.pendingThreadArgs.append(args)

    return thread

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

  def on_thread(self, thread, name, callback):
    self.on('__thread_%s_%s' % (name, thread.uuid), callback)

