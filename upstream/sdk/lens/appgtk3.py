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

# GTK
from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version('WebKit2', '4.0')
from gi.repository import WebKit2, Gio, Gtk, GObject, Gdk

logger = logging.getLogger('Lens.Backend.Gtk3')

class ThreadManagerGtk3(ThreadManager):
    def __init__(self, maxConcurrentThreads=10):
        ThreadManager.__init__(self, maxConcurrentThreads)

        # watch the queue for updates
        _fd = self.queue_in._reader.fileno()

        GObject.io_add_watch(_fd, GObject.IO_IN, self._on_cb)

    def _on_cb(self, fd, cond):
        while not self.queue_in.empty():
            data = self.queue_in.get()

            if data['name'] == '__completed':
                self._thread_completed(self.threads[data['uuid']]['t'])

            else:
                self.emit('__thread_%s_%s' % (data['uuid'], data['name']), self.threads[data['uuid']], *data['args'])

        return True


class _WebView(WebKit2.WebView):
    """
    """

    __gsignals__ = {
        'on-js': (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_STRING,GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, inspector=False):
        WebKit2.WebView.__init__(self)

        self.__inspector = inspector

        self._uri_app_base = '/'
        self._uri_lens_base = '/'

        # register signals
        self.connect('decide-policy', self._decide_policy_cb)
        self.connect('load-changed', self._load_changed_cb)
        self.connect('notify::title', self._title_changed_cb)

        # register custom uri schemes for app:// and lens://
        context = WebKit2.WebContext.get_default()
        context.register_uri_scheme('app', self._uri_resource_app_cb)
        context.register_uri_scheme('lens', self._uri_resource_lens_cb)

        sm = context.get_security_manager()
        sm.register_uri_scheme_as_cors_enabled('app')
        sm.register_uri_scheme_as_cors_enabled('lens')

        #: don't need access to the context menu when not inspecting the app
        if not inspector:
            self.__context_menu_id = self.connect('context-menu', self._context_menu_cb)

        self.l_uri = None

        enable_settings = ['enable-accelerated-2d-canvas', 'enable-smooth-scrolling', 'javascript-can-access-clipboard']

        for setting in enable_settings:
            try:
                self.get_settings().set_property(setting, True)
            except:
                pass

        if inspector:
            try:
                self.get_settings().set_property('enable-developer-extras', True)
            except:
                pass

    def _context_menu_cb(self, view, context_menu, event, hit_test_result):
        return True

    def _decide_policy_cb(self, view, decision, decision_type):
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:

            # grab the requested URI
            uri = decision.get_request().get_uri()

    def _load_changed_cb(self, view, event):
        pass

    def _title_changed_cb(self, view, event):
        _in = view.get_title()

        # check for "_BR::" leader to determine we're crossing
        # the python/JS bridge
        if _in is None or not _in.startswith('_BR::'):
            return

        try:
            _in = json.loads(_in[5:])

            _name = _in.setdefault('name', '')
            _args = _in.setdefault('args', [])

            # emit our python/js bridge signal
            self.emit('on-js', _name, _args)

        except:
            pass

    def _uri_resource_app_cb(self, request):
        path = o = request.get_uri().split('?')[0]

        if path == 'app:///':
            path = self._uri_app_base + 'app.html'

        else:
            path = path.replace('app://', self._uri_app_base)

            # variable substitution
            path = path.replace('$backend', 'gtk3')

        logger.debug('Loading app resource: {0} ({1})'.format(o, path))

        if os.path.exists(path):
            request.finish(Gio.File.new_for_path(path).read(None), -1, Gio.content_type_guess(path, None)[0])

        else:
            raise Exception('App resource path not found: {0}'.format(path))

    def _uri_resource_lens_cb(self, request):
        path = o = request.get_uri().split('?')[0]
        path = path.replace('lens://', self._uri_lens_base)

        # make lens.css backend specific
        path = path.replace('lens.css', 'lens-gtk3.css')

        logger.debug('Loading lens resource: {0} ({1})'.format(o, path))

        if os.path.exists(path):
            request.finish(Gio.File.new_for_path(path).read(None), -1, Gio.content_type_guess(path, None)[0])

        else:
            raise Exception('Lens resource path not found: {0}'.format(path))

    def set_inspector(self, state):
        if state == self.__inspector:
            return

        try:
            self.get_settings().set_property('enable-developer-extras', state)
        except:
            pass

        #: need access to the context menu to inspect the app
        if state:
            self.disconnect(self.__context_menu_id)

        else:
            self.__context_menu_id = self.connect('context-menu', self._context_menu_cb)

        self.__inspector = state


class ViewGtk3(View):


    def __init__(self, name="MyLensApp", width=640, height=480, inspector=False, start_maximized=False, *args, **kwargs):
        View.__init__(self, name=name, width=width, height=height, *args, **kwargs)
        # prepare Gtk dbus mainloop
        DBusGMainLoop(set_as_default=True)

        self._app_loaded = False

        self._logger = logging.getLogger('Lens.ViewGtk3')
        self._manager = ThreadManagerGtk3()

        self._inspector = inspector
        self._start_maximized = start_maximized
        self._window_state = {}
        self._build_app()

    def _build_app(self):
        # build window
        self._window = w = Gtk.Window()

        self.set_title(self._app_name)
        self.set_size(self._app_width, self._app_height)

        # center on screen
        w.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        # build and add webkit container
        self._lensview = lv = _WebView(inspector=self._inspector)
        w.add(lv)

        # connect to Gtk signals
        lv.connect('on-js', self._on_js)
        lv.connect('load-changed', self._load_change_cb)
        w.connect('delete-event', self._delete_event_cb)
        w.connect('window-state-event', self._window_state_event_cb)

        # connect to Lens signals
        self.on('__close_app', self._close_cb)

    def _close_cb(self, *args):
        self.emit('app.close')
        Gtk.main_quit(*args)

    def _delete_event_cb(self, *args):
        self.emit('__close_app', *args)

    def _window_state_event_cb(self, window, event, *args):
        self._window_state["maximized"] = event.new_window_state & Gdk.WindowState.MAXIMIZED
        self._window_state["fullscreen"] = event.new_window_state & Gdk.WindowState.FULLSCREEN

    def _load_change_cb(self, view, event):
        # show window once some page has loaded
        if( event == WebKit2.LoadEvent.FINISHED ):
            self._window.show_all()
            if self._start_maximized:
                self.toggle_window_maximize()
            if not self._app_loaded:
                self._app_loaded = True
                self.emit('app.loaded')

    def _run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

    def emit_js(self, name, *args):
        self._lensview.run_javascript(self._javascript % json.dumps([name] + list(args)), None, None, None)

    def load_string(self, data):
        self._lensview.load_html(data, self._lensview._uri_app_base)

    def load_uri(self, uri):
        # TODO: we require webkitgtk3 2.2.7 or later
        #
        self._lensview._uri_app_base = os.path.dirname(uri) + '/'
        self._lensview.load_uri('app:///')

    def set_inspector(self, state):
        self._lensview.set_inspector(state)

    def set_size(self, width, height):
        logger.debug('Setting app size: {0}x{1}'.format(width, height))
        self._window.set_size_request(width, height)
        self._window.set_default_size(width, height)

    def set_title(self, title):
        self._window.set_title(title)
        self._window.set_wmclass(title, title)

    def set_uri_app_base(self, uri):
        self._lensview._uri_app_base = uri

    def set_uri_lens_base(self, uri):
        self._lensview._uri_lens_base = uri

    def toggle_window_maximize(self):
        if self._window_state.get("maximized", False):
            self._window.unmaximize()
            self.emit_js('window-unmaximized')
        else:
            self._window.maximize()
            self.emit_js('window-maximized')

    def toggle_window_fullscreen(self):
        if self._window_state.get("fullscreen", False):
            self._window.unfullscreen()
            self.emit_js('window-unfullscreen')
        else:
            self._window.fullscreen()
            self.emit_js('window-fullscreen')
