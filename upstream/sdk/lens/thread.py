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

import logging
import multiprocessing
import time
import traceback

from lens.view import EventEmitter

__counter = 0
def _new_name():
    global __counter
    __counter += 1
    return "LensThread-{}-{}".format(__counter, time.time())



class Thread(EventEmitter):
    def __init__(self, daemon=False):
        EventEmitter.__init__(self)

        self._daemon = daemon

        # the ID won't change when the name changes
        self._uuid = _new_name()


    @property
    def daemon(self):
        return self._daemon

    @daemon.setter
    def daemon(self, state):
        self._daemon = bool(state)

    @property
    def uuid(self):
        return self._uuid

    def run(self):
        pass



class ThreadProcess(multiprocessing.Process):
    def __init__(self, thread, pipe_in, queue_out):
        multiprocessing.Process.__init__(self)

        self._thread = thread
        self._uuid = thread.uuid
        self.daemon = thread.daemon

        self._thread.on_any(self._thread_signal_cb)

        self._pipe_in = pipe_in
        self._queue_out = queue_out

    def _thread_signal_cb(self, name, *args):
        self._queue_out.put({
            'uuid': self.uuid,
            'name': name,
            'args': list(args)
        })

    @property
    def uuid(self):
        return self._uuid

    def run(self):

        self._thread.run()

        self._queue_out.put({
            'uuid': self.uuid,
            'name': '__completed'
        })



class ThreadManager(EventEmitter):
    """
    Manages many LensThreads. This involves starting and stopping
    said threads, and respecting a maximum num of concurrent threads limit
    """
    def __init__(self, maxConcurrentThreads=5):
        EventEmitter.__init__(self)

        self._logger = logging.getLogger('Lens.ThreadManager')

        #stores all threads, running or stopped
        self.threads = {}
        self.pendingThreadArgs = []
        self.maxConcurrentThreads = maxConcurrentThreads

        self.queue_in = multiprocessing.Queue()


    def _thread_completed(self, thread):
        """
        Decrements the count of concurrent threads and starts any
        pending threads if there is space
        """

        #: unsubscribe all signals to the thread
        if self.threads[thread.uuid]['u']:
            self.unsubscribe_like('__thread_%s_' % (thread.uuid))

        del(self.threads[thread.uuid])
        running = len(self.threads) - len(self.pendingThreadArgs)

        self._logger.debug("%s completed. %s running, %s pending" % (thread, running, len(self.pendingThreadArgs)))

        if running < self.maxConcurrentThreads:
            try:
                uuid = self.pendingThreadArgs.pop()

                self._logger.debug("Starting pending %s" % self.threads[uuid])
                self.threads[uuid]['t'].start()
                self.emit('__thread_%s_started' % (uuid), self.threads[uuid])
                self.emit('__thread_%s_state' % (uuid), self.threads[uuid], 'started')

            except IndexError:
                pass

            except:
                self._logger.warn('Caught exception!\n%s', traceback.format_exc())

    def _register_thread_signals(self, thread, *args):
        pass

    def add(self, thread, unsubscribe=True):
        # TODO: be nicer
        if not isinstance(thread, Thread):
            raise TypeError("not a LensThread stupiD!")

        running = len(self.threads) - len(self.pendingThreadArgs)

        _pipe = None
        _thread = ThreadProcess(thread, _pipe, self.queue_in)

        uuid = _thread.uuid

        if uuid not in self.threads:
            self.threads[uuid] = {
                't': _thread,
                'p': _pipe,
                'u': unsubscribe
            }

            self._register_thread_signals(_thread)

            state = 'added'

            if running < self.maxConcurrentThreads:
                self._logger.debug("Starting %s" % _thread)
                self.threads[uuid]['t'].start()
                state = 'started'
                self.emit('__thread_%s_started' % (uuid), thread)

            else:
                self._logger.debug("Queing %s" % thread)
                self.pendingThreadArgs.append(uuid)
                state = 'queued'
                self.emit('__thread_%s_queued' % (uuid), thread)

            self.emit('__thread_%s_state' % (uuid), thread, state)

    # DEPRECATE:
    # use add() method instead, remove in reference in 1.0.0
    def add_thread(self, thread, unsubscribe=True):
        self._logger.warn('The "add_thread()" method is deprecated, use "add()" instead.')
        self.add(thread, unsubscribe)

    def on(self, thread, name, callback):
        EventEmitter.on(self, '__thread_%s_%s' % (thread.uuid, name), callback)

    # DEPRECATE:
    # use on() method instead, remove in 1.0.0
    def on_thread(self, thread, name, callback):
        self._logger.warn('The "on_thread()" method is deprecated, use "on()" instead.')
        self.on(thread, name, callback)

