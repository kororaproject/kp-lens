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
import mimetypes

import pathlib

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
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineProfile, QWebEngineScript, QWebEngineView
from PyQt5.QtWebChannel import *

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


class AppSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self,):
        super().__init__()
        self._uri_app_base = '/'

    def requestStarted(self, request):
        path = o = request.requestUrl().toString()
        if path == 'app:///':
            path = self._uri_app_base + 'app.html'
            logger.debug('Loading app resource: {0} ({1})'.format(o, path))

        elif path.startswith('app://'):
            path = path.replace('app://', self._uri_app_base)
            logger.debug('Loading app resource: {0} ({1})'.format(o, path))

            # variable substitution
            path = path.replace('$backend', 'qt5')

        request.redirect(QUrl(QString(path)))

class LensSchemeHandler(QWebEngineUrlSchemeHandler):
    def __init__(self):
        super().__init__()
        self._uri_lens_base = '/'

    def requestStarted(self, request):
        path = o = request.requestUrl().toString()
        path = path.replace('lens://', self._uri_lens_base)

        path = path.replace('lens.css', 'lens-qt5webengine.css')

        logger.debug('Loading lens resource: {0} ({1})'.format(o, path))


        request.redirect(QUrl(QString(path)))


class _QWebView(QWebEngineView):
    def __init__(self, inspector=False):
        QWebEngineView.__init__(self)

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


class _QWebPage(QWebEnginePage):
    def __init__(self, debug=False):
        QWebEnginePage.__init__(self)


class ViewQt5WebEngine(View, QObject):
    _emit_js_signal = pyqtSignal(str, QVariant);

    def __init__(self, name="MyLensApp", width=640, height=480, inspector=False, start_maximized=False, *args, **kwargs):
        View.__init__(self, name=name, width=width,height=height, *args, **kwargs)
        QObject.__init__(self)

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
        if self._inspector:
            os.environ.setdefault('QTWEBENGINE_REMOTE_DEBUGGING', '8001')

        # build webengine container
        self._lensview = lv = _QWebView(inspector=self._inspector)
        self._page = p = _QWebPage()
        lv.setPage(self._page)

        # connect to Qt signals
        lv.loadFinished.connect(self._loaded_cb)
        self._app.lastWindowClosed.connect(self._last_window_closed_cb)

        # build webchannel script and inject
        qwebchannel_js = QFile(':/qtwebchannel/qwebchannel.js')
        if not qwebchannel_js.open(QIODevice.ReadOnly):
                raise SystemExit('Failed to load qwebchannel.js with error: %s' % qwebchannel_js.errorString())
        qwebchannel_js = bytes(qwebchannel_js.readAll()).decode('utf-8')

        script = QWebEngineScript()
        script.setSourceCode(qwebchannel_js + '''
                window.lens = window.lens || {};
                window.lens._channel = new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.lens.emit = function() {
                        var args = Array.prototype.slice.call(arguments);
                        if (args.length > 0) {
                            channel.objects.bridge._from_bridge(args);
                        }
                    };

                    channel.objects.bridge._emit_js_signal.connect(function(name, args) {
                        window.lens.__broadcast(name, args);
                    });
                });
            ''')
        script.setName('lens-bridge')
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setRunsOnSubFrames(True)

        p.profile().scripts().insert(script)

        self._channel = QWebChannel(p)
        p.setWebChannel(self._channel)
        self._channel.registerObject('bridge', self)

        # set up scheme handlers for app:// and lens://
        self._app_scheme_handler = AppSchemeHandler()
        self._lens_scheme_handler = LensSchemeHandler()

        self._profile = QWebEngineProfile().defaultProfile()
        self._profile.installUrlSchemeHandler('app'.encode(), self._app_scheme_handler)
        self._profile.installUrlSchemeHandler('lens'.encode(), self._lens_scheme_handler)

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

    @pyqtSlot(QVariant)
    def _from_bridge(self, name_args):
        # emit our python/js bridge signal
        self.emit(name_args[0], *name_args[1:])

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

    def _run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self._app.exec_()

    def emit_js(self, name, *args):
        self._emit_js_signal.emit(name, list(args))

    def load_string(self, data):
        index_uri = pathlib.Path(self._app_scheme_handler._uri_app_base).as_uri()
        self._lensview.setHtml(data, QUrl(index_uri))

    def load_uri(self, uri):
        uri_base = os.path.dirname(uri) + '/'
        self.set_uri_app_base(uri_base)
        path = uri_base + 'app.html'

        stream = QFile(path)
        if stream.open(QFile.ReadOnly):
            data = str(stream.readAll(), 'utf-8')
            index_uri = pathlib.Path(uri_base).as_uri()
            logger.debug('Using {0} as index URI'.format(index_uri))
            self._lensview.setHtml(data, QUrl(index_uri))

    def set_inspector(self, state):
        self._lensview.set_inspector(state)

    def set_size(self, width, height):
        logger.debug('Setting app size: {0}x{1}'.format(width, height))
        self._lensview.setMinimumSize(width, height)
        self._lensview.resize(width, height)

    def set_title(self, title):
        self._lensview.setWindowTitle(QString(title))

    def set_uri_app_base(self, uri):
        self._app_scheme_handler._uri_app_base = pathlib.Path(uri).as_uri() + "/"

    def set_uri_lens_base(self, uri):
        self._lens_scheme_handler._uri_lens_base = pathlib.Path(uri).as_uri() + "/"

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
