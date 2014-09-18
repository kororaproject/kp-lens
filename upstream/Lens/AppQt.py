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
import json
import signal

from Lens.View import View
from Lens.Thread import Thread, ThreadManager

# Qt4
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *



class ThreadManagerQt(ThreadManager):
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
        self.emit('__thread_%s_%s' % (data['name'], data['uuid']), self.threads[data['uuid']], *data['args'])

    return True



class _QWebView(QWebView):


  def __init__(self):
    QWebView.__init__(self)

  def contextMenuEvent(self, event):
    event.ignore()



class _QWebPage(QWebPage):


  def __init__(self):
    QWebView.__init__(self)

  def javaScriptConsoleMessage(self, message, line, source_id):
    print("%s: %s (%s)" % (line, message, source_id))



class ViewQt(View):


  def __init__(self, *args, **kwargs):
    View.__init__(self, *args, **kwargs)

    self._app = QApplication([])
    self._logger = logging.getLogger('Lens.ViewQt')
    self._manager = ThreadManagerQt(app=self._app)

    self._build_app()

  def _build_app(self):
    # build webkit container
    self._lensview = lv = _QWebView()
    lv.setPage(_QWebPage())

    self._frame = lv.page().mainFrame()

    # connect to Qt signals
    lv.titleChanged.connect(self._title_changed_cb)
    self._app.lastWindowClosed.connect(self._last_window_closed_cb)

    # connect to Lens signals
    self.on('__close_app', self._close_cb)

    self.set_title(self._app_name)
    self.set_size(self._app_width, self._app_height)

    # center on screen
    _frame_geometry = lv.frameGeometry()
    _active_screen = self._app.desktop().screenNumber(self._app.desktop().cursor().pos())
    _center = self._app.desktop().screenGeometry(_active_screen).center()
    _frame_geometry.moveCenter(_center)
    lv.move(_frame_geometry.topLeft())

    lv.show()

  def _close_cb(self):
    self._app.exit()

  def _last_window_closed_cb(self, *args):
    self.emit('__close_app', *args)

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
    self._logger.debug("Loading URI: %s" % uri)

    # load our index file
    self._lensview.load(QUrl(uri))

  def set_size(self, width, height):
    self._lensview.setFixedSize(width, height)

  def set_title(self, title):
    self._lensview.setWindowTitle(QString(title))

