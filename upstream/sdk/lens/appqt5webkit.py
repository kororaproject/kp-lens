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

import json
import logging
import os
import signal

from lens.view import View
from lens.thread import Thread, ThreadManager

logger = logging.getLogger('Lens.Backend.Qt5')

# Qt5
try:
    from dbus.mainloop.pyqt5 import DBusQtMainLoop

except ImportError:
    # TODO: validate we're not might be windows
    pass

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKitWidgets import *
from PyQt5.QtWebChannel import *
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

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


class CustomNetworkAccessManager(QNetworkAccessManager):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._uri_app_base = ''
        self._uri_lens_base = ''

    def createRequest(self, operation, request, device):
        path = o = request.url().toString()

        if path.startswith('app://') or path.startswith('lens://'):
            if path == 'app:///':
                path = 'file://' + self._uri_app_base + 'app.html'
                logger.debug('Loading app resource: {0} ({1})'.format(o, path))

            elif path.startswith('app://'):
                path = path.replace('app://', 'file://' + self._uri_app_base)
                logger.debug('Loading app resource: {0} ({1})'.format(o, path))

                # variable substitution
                path = path.replace('$backend', 'qt5')

            elif path.startswith('lens://'):
                path = path.replace('lens://', 'file://' + self._uri_lens_base)
                logger.debug('Loading lens resource: {0} ({1})'.format(o, path))

                # make lens.css backend specific
                path = path.replace('lens.css', 'lens-qt5.css')

            request.setUrl(QUrl(QString(path)))

        return QNetworkAccessManager.createRequest(self, operation, request, device)


class _QWebView(QWebView):
    def __init__(self, inspector=False):
        QWebView.__init__(self)

        self.__inspector = None
        self.__contextMenuEvent = self.contextMenuEvent

        self.set_inspector(inspector)

    def ignoreContextMenuEvent(self, event):
        event.ignore()

    def set_inspector(self, state):
        if state == self.__inspector:
            return

        if state:
            self.contextMenuEvent = self.__contextMenuEvent

        # disable context menu if inspector not enabled
        else:
            self.contextMenuEvent = self.ignoreContextMenuEvent

        self.__inspector = state


class _QWebPage(QWebPage):
    def __init__(self, debug=False):
        QWebView.__init__(self)


class ViewQt5WebKit(View):
    def __init__(self, name="MyLensApp", width=640, height=480, inspector=False, start_maximized=False, *args, **kwargs):
        View.__init__(self, name=name, width=width,height=height, *args, **kwargs)

        self._app = QApplication([])

        # prepare Qt DBus mainloop
        try:
            DBusQtMainLoop(set_as_default=True)

        except NameError:
            # TODO: validate DBus failed to import (windows)
            pass

        self._app_loaded = False

        self._manager = ThreadManagerQt5(app=self._app)

        self._inspector = inspector
        self._start_maximized = start_maximized
        self._build_app()

    def _build_app(self):
        # build webkit container
        self._lensview = lv = _QWebView(inspector=self._inspector)
        lv.setPage(_QWebPage())

        if self._inspector:
            lv.settings().setAttribute(lv.settings().DeveloperExtrasEnabled, True)

        self._frame = lv.page().mainFrame()

        # connect to Qt signals
        lv.loadFinished.connect(self._loaded_cb)
        lv.titleChanged.connect(self._title_changed_cb)
        self._app.lastWindowClosed.connect(self._last_window_closed_cb)

        self._channel = QWebChannel(lv.page())
#        lv.page().setWebChannel(self._channel)
#        self.channel.registerObject(foo)

        #
        self._cnam = CustomNetworkAccessManager()
        lv.page().setNetworkAccessManager(self._cnam)

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
        self._frame.evaluateJavaScript(QString(self._javascript % json.dumps([name] + list(args))))

    def load_uri(self, uri):
        uri_base = os.path.dirname(uri) + '/'
        self.set_uri_app_base(uri_base)
        path = uri_base + 'app.html'

        stream = QFile(path)
        if stream.open(QFile.ReadOnly):
            data = str(stream.readAll(), 'utf-8')
            self._lensview.setHtml(data, QUrl('file://' + uri_base))

    def set_inspector(self, state):
        self._lensview.set_inspector(state)

    def set_size(self, width, height):
        logger.debug('Setting app size: {0}x{1}'.format(width, height))
        self._lensview.setMinimumSize(width, height)
        self._lensview.resize(width, height)

    def set_title(self, title):
        self._lensview.setWindowTitle(QString(title))

    def set_uri_app_base(self, uri):
        self._cnam._uri_app_base = uri

    def set_uri_lens_base(self, uri):
        self._cnam._uri_lens_base = uri

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
