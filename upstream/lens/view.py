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

import logging

class EventEmitter():
  def __init__(self):
    self.__events = {}
    self.__events_once = {}

    self._logger = logging.getLogger('Lens.EventEmitter')

  def catch(self, callback=None):
    if self.on('error', callback) is not None:
      return self

  def emit(self, name, *args, **kwargs):
    s = self.__events.get(name, [])        # subscribers
    so = self.__events_once.pop(name, [])  # subscribers - once only
    gs = self.__events.get('__*', [])      # global subscribers

    self._logger.debug('Emit %s in %s (%d, %d)' % (name, self, len(s)+len(so), len(gs)))

    # specific (including once only) subscribers
    for cb in s + so:
      cb(*args, **kwargs)

    # global subscribers
    for cb in gs:
      cb(name, *args, **kwargs)

  def has_subscribers(self, name):
    return len(self.subscribers()) > 0

  def on(self, name, callback):
    self._logger.debug('Subscribing %s on %s' % (name, callback))
    self.__events.setdefault(name, []).append(callback)

    return callback

  def on_any(self, callback):
    self._logger.debug('Subscribing %s on any signal' % (callback))
    self.__events.setdefault('__*', []).append(callback)

    return callback

  def once(self, name, callback):
    self._logger.debug('Subscribing %s on %s for one time only' % (name, callback))
    self.__events_once.setdefault(name, []).append(callback)

    return callback

  def subscribers(self, name):
    return self.__events.get(name, []) + self.__events_once.get(name, []) + self.__events.get('__*', [])

  def unsubscribe(self, name, callback=None):
    # remove only the specified callback
    if callback is not None:
      self.__events[name] = [e for e in self.__events.get(name, []) if e != callback]

      if not self.__events[name]:
        self.__events.pop(name, None)

    # remove all subscriptions
    else:
      self.__events.pop(name, None)

  def unsubscribe_like(self, like):
    # filter out any subscriptions based on "like"-ness
    self.__events = {k:self.__events[k] for k in self.__events if like not in k}



class View(EventEmitter):


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

  def set_system_theme(self, theme):
    self._system_theme = theme

  def set_title(self, name, message):
    raise NotImplementedError('Method "set_title" needs to be subclassed.')

  def toggle_window_maximize(self):
    raise NotImplementedError('Method "toggle_window_maximize" needs to be subclassed.')

  def toggle_window_fullscreen(self):
    raise NotImplementedError('Method "toggle_window_fullscreen" needs to be subclassed.')
