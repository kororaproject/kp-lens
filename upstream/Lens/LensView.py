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

class EventEmitter():
  def __init__(self):
    self.__events = {}

  def catch(self, callback=None):
    if self.on('error', callback) is not None:
      return self

  def emit(self, name, *args, **kwargs):
    s = self.__events.get(name, [])
    gs = self.__events.get('__*', [])

    if not s:
      # TODO: debug print only
      print('-- Emit %s in %s (0)' % (name, self))

    else:
      # TODO: debug print only
      print('-- Emit %s in %s (%d)' % (name, self, len(s)))

      for cb in s:
        cb(*args, **kwargs)

    # global subscribers
    if len(gs):
      for cb in gs:
        cb(name, *args, **kwargs)


  def emit_safe(self, name):
    pass

  def has_subscribers(self, name):
    return len(self.subscribers) > 0

  def on(self, name, callback):
    print('-- Subscribing %s on %s' % (name, callback))

    self.__events.setdefault(name, []).append(callback)

    return callback

  def on_any(self, callback):
    print('-- Subscribing %s on any signal' % (callback))

    self.__events.setdefault('__*', []).append(callback)

    return callback

  def once(self, name, callback):
    pass

  def subscribers(self, name):
    return self.__events.get(name, [])

  def unsubscribe(self, name, callback=None):
    # remove only the specified callback
    if callback is not None:
      self.__events[name] = [e for e in self.__events.get(name, []) if e != callback]

      if not self.__events[name]:
        self.__events.pop(name, None)

    # remove all subscriptions
    else:
      self.__events.pop(name, None)



class LensView(EventEmitter):


  def __init__(self, name="MyLensApp", width=640, height=480, *args, **kwargs):
    EventEmitter.__init__(self)

    self._app_name = name
    self._app_width = width
    self._app_height = height

  def _build_app(self):
    raise NotImplementedError('Method "_build_app" needs to be subclassed.')

  def _on_js(self, thread, name, args):
    self.emit(name, *args)

  def close(self, *args, **kwargs):
    self.emit('__close_app')

  def emit_js(self, name, *args):
    raise NotImplementedError('Method "emit_js" needs to be subclassed.')

  def load_uri(self, uri):
    raise NotImplementedError('Method "load_uri" needs to be subclassed.')

  def set_size(self, name, message):
    raise NotImplementedError('Method "set_size" needs to be subclassed.')

  def set_title(self, name, message):
    raise NotImplementedError('Method "set_title" needs to be subclassed.')

