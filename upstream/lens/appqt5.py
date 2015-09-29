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

import json
import logging
import os
import signal

from lens.view import View
from lens.thread import Thread, ThreadManager

# Qt4
from dbus.mainloop.qt import DBusQtMainLoop
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import *

# FIXME: QString does not exists in python3
try:
  from PyQt5.QtCore import QString
except ImportError:
  QString = type("")


class ThreadManagerQt5(ThreadManager):
  def __init__(self, app=None, maxConcurrentThreads=10):
    ThreadManager.__init__(self, maxConcurrentThreads)

    self._app = app

    if self._app is not None:

      # watch the queue for updates
      _fd = self.queue_in._reader.fileno()

      _notifier = QSocketNotifier(_fd, QSocketNotifier.Read, self._app)
      _notifier.activated.connect(self._on_cb)

  def _on_cb(self, fd):
    while not self.queue_in.empty():
      data = self.queue_in.get()

      if data['name'] == '__completed':
        self._thread_completed(self.threads[data['uuid']]['t'])

      else:
        self.emit('__thread_%s_%s' % (data['uuid'], data['name']), self.threads[data['uuid']], *data['args'])

    return True



class _QWebView(QWebView):
  def __init__(self, inspector=False):
    QWebView.__init__(self)
    self._inspector = inspector

    # disable context menu if inspector not enabled
    if not inspector:
      self.contextMenuEvent = self.ignoreContextMenuEvent

  def ignoreContextMenuEvent(self, event):
    event.ignore()


class _QWebPage(QWebPage):
  def __init__(self, debug=False):
    QWebView.__init__(self)


class ViewQt5(View):
  def __init__(self, name="MyLensApp", width=640, height=480, inspector=False, start_maximized=False, *args, **kwargs):
    View.__init__(self, name=name, width=width,height=height, *args, **kwargs)
    # prepare Qt dbus mainloop
    DBusQtMainLoop(set_as_default=True)
    self._app = QApplication([])

    self._app_loaded = False

    self._logger = logging.getLogger('Lens.ViewQt')
    self._manager = ThreadManagerQt5(app=self._app)

    self._inspector = inspector
    self._start_maximized = start_maximized
    self._build_app()

  def _build_app(self):
    # build webkit container
    self._lensview = lv = _QWebView(inspector=self._inspector)
    lv.setPage(_QWebPage())

    if self._inspector:
      lv.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)

    self._frame = lv.page().mainFrame()

    # connect to Qt signals
    lv.loadFinished.connect(self._loaded_cb)
    lv.titleChanged.connect(self._title_changed_cb)
    self._app.lastWindowClosed.connect(self._last_window_closed_cb)

    # connect to Lens signals
    self.on('__close_app', self._close_cb)

    # center on screen
    _frame_geometry = lv.frameGeometry()
    _active_screen = self._app.desktop().screenNumber(self._app.desktop().cursor().pos())
    _center = self._app.desktop().screenGeometry(_active_screen).center()
    _frame_geometry.moveCenter(_center)
    lv.move(_frame_geometry.topLeft())

    self.set_title(self._app_name)
    self.set_size(self._app_width, self._app_height)

  def _close_cb(self):
    self.emit('app.close')
    self._app.exit()

  def _last_window_closed_cb(self, *args):
    self.emit('__close_app', *args)

  def _loaded_cb(self, success):
    # show window once some page has loaded
    self._lensview.show()
    if self._start_maximized:
      self.toggle_window_maximize()


    if not self._app_loaded:
      self._app_loaded = True
      self.emit('app.loaded')

  def _title_changed_cb(self, title):
    _in = str(title)

    # check for "_BR::" leader to determine we're crossing
    # the python/JS bridge
    if _in is None or not _in.startswith('_BR::'):
      return

    try:
      _in = json.loads(_in[5:])

      _name = _in.setdefault('name', '')
      _args = _in.setdefault('args', [])

    except:
      return

    # emit our python/js bridge signal
    self.emit(_name, *_args)

  def _run(self):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    self._app.exec_()

  def emit_js(self, name, *args):
    self._frame.evaluateJavaScript(QString("var _rs = angular.element(document).scope(); _rs.safeApply(function(){_rs.$broadcast.apply(_rs,%s)});" % json.dumps([name] + list(args))))

  def load_uri(self, uri):
    # FIXME
    # improve resource handling of lens:// schemas by intercepting resources
    # via WebKitWebPage (extensions) send-request(). Not yet exposed in python
    #
    # for now we emulate the effect with a replace
    uri_base = os.path.dirname(uri) + '/'
    html = open(uri.replace('file://',''), 'r').read()
    html = html.replace('lens://', self._uri_lens_base)
    html = html.replace('app://', uri_base)

    # replace system theming
    html = html.replace('<style type="system" />', self._system_theme)

    self._lensview.setHtml(QString(html), QUrl(uri_base))

  def set_size(self, width, height):
    self._lensview.setMinimumSize(width, height)
    self._lensview.resize(width, height)

  def set_title(self, title):
    self._lensview.setWindowTitle(QString(title))

  def toggle_window_maximize(self):
    if self._lensview.windowState() & Qt.WindowMaximized:
      self._lensview.setWindowState(self._lensview.windowState() ^ Qt.WindowMaximized)
      self.emit_js('window-unmaximized')
    else:
      self._lensview.setWindowState(self._lensview.windowState() | Qt.WindowMaximized)
      self.emit_js('window-maximized')

  def toggle_window_fullscreen(self):
    if self._lensview.windowState() & Qt.WindowFullScreen:
      self._lensview.setWindowState(self._lensview.windowState() ^ Qt.WindowFullScreen)
      self.emit_js('window-unfullscreen')
    else:
      self._lensview.setWindowState(self._lensview.windowState() | Qt.WindowFullScreen)
      self.emit_js('window-fullscreen')
