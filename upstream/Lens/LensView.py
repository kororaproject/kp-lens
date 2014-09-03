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

import pprint

class EventEmitter():
  def __init__(self):
    self._events = {}

  def catch(self, callback=None):
    if self.on('error', callback) is not None:
      return self

  def emit(self, name, *args, **kwargs):
    s = self._events.get(name, [])

    if not s:
      # TODO: debug print only
      print('-- Emit %s in %s (0)' % (name, self))

    else:
      # TODO: debug print only
      print('-- Emit %s in %s (%d)' % (name, self, len(s)))

      for cb in s:
        cb(*args, **kwargs)

  def emit_safe(self, name):
    pass

  def has_subscribers(self, name):
    return len(self.subscribers) > 0

  def on(self, name, callback):
    print('-- Subscribing %s on %s' % (name, callback))

    self._events.setdefault(name, []).append(callback)


    return callback

  def once(self, name, callback):
    pass

  def subscribers(self, name):
    return self._events.get(name, [])


  def unsubscribe(self, name, callback=None):
    # remove only the specified callback
    if callback is not None:
      self._events[name] = [e for e in self._events.get(name, []) if e != callback]

      if not self._events[name]:
        self._events.pop(name, None)

    # remove all subscriptions
    else:
      self._events.pop(name, None)


class LensView(EventEmitter):
  def close(self, *args, **kwargs):
    self.emit('__close_app')

  def emitJS(self, name, message):
    raise NotImplementedError('This needs to be subclassed: emitJS')
    pass

  def loadURI(self, uri):
    raise NotImplementedError('This needs to be subclassed: loadURI')
    pass

  def _onJS(self, thread, name, args):
    self.emit(name, *args)

