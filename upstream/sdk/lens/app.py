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

try:
    import dbus
except ImportError:
    # might be windows...
    pass

import logging
import os
import sys
import subprocess
import traceback

from lens.view import View
from lens.thread import Thread, ThreadManager

logger = logging.getLogger('Lens.App')

class App():
    """The app object implements a Lens application and acts as the central
    object. Once created it will act as a central registry for the view
    toolkit abstraction, thread management, signal handling and much more.

    :param toolkit: force the toolkit to use. If set to `None` the toolkit
                    will be auto detected.
    :param toolkit_hint: hint to the preferred toolkit if the auto detection
                         fails to determine the active toolkit.
    :param custom_toolkits: Additional or overriding toolkit class definitions.
    :param name: the name of the Lens application. Also shown in the Lens
                 application window's title bar.
    :param width: the width of the Lens applciation window. Defaults to 640.
    :param height the height of the Lens applciation window. Defaults to 480.
    """
    def __init__(self, toolkit=None, toolkit_hint='gtk', custom_toolkits={}, name="MyLensApp", *args, **kwargs):
        self.custom_toolkits = custom_toolkits
        self._app_name = name
        self._app_width = kwargs.get('width', 640)
        self._app_height = kwargs.get('height', 480)

        self._start_maximized = kwargs.get('start_maximized', False)

        #: check environment for inspector overrides
        self._inspector = False
        if os.environ.get('LENS_INSPECTOR') == '1':
            self._inspector = kwargs.get('inspector', True)

        #: check environment for debug overrides
        if os.environ.get('LENS_DEBUG') == '1':
            logging.basicConfig(level=logging.DEBUG)

        #: check environment for toolkit overrides
        toolkit = os.environ.get('LENS_TOOLKIT', toolkit)

        # dbus
        self._dbus_session = None
        self._dbus_system = None

        #: find lens data path
        base = None
        logger.debug("Current working directory %s", os.getcwd())
        sdk_path = os.path.join(os.path.dirname(__file__), '../lens-data')
        for d in [sdk_path, '/usr/share/lens']:
            if os.path.exists(d):
                if d.startswith('/'):
                    base = d
                else:
                    base = os.path.join(os.getcwd(), d)
                break

        if base is None:
            raise Exception('Unable to locate lens base data for UI components.')

        self._uri_base = os.path.abspath(base)

        self.__load_toolkit(toolkit, toolkit_hint)

        #: manage directory namespaces for local app data
        self.namespaces = []

    def __get_desktop_hint(self, hint="gnome"):
        def __is_running(process):
            try:
                # Linux/Unix
                s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
            except:
                # Windows
                s = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)

            for x in s.stdout:
                if process in x.decode('utf-8'):
                    return True

            return False

        desktop = hint

        if os.environ.get('KDE_FULL_SESSION') == 'true':
            desktop = 'kde'

        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            desktop = 'gnome'

        elif __is_running("xfce-mcs-manage") or __is_running('xfce4-session'):
            desktop = 'xfce'

        elif __is_running("ksmserver"):
            desktop = 'kde'

        elif __is_running("svchost.exe"):
            desktop = "windows"

        return desktop

    def __get_desktop_toolkit_hint(self, hint):
        toolkit = hint
        desktop = self.__get_desktop_hint()

        if desktop in ['kde']:
            toolkit = 'qt'

        elif desktop in ['gnome', 'mate', 'xfce']:
            toolkit = "gtk"

        elif desktop in ['windows']:
            toolkit = 'qt5webengine'

        return toolkit

    def __get_desktop_theme(self):
        desktop = self.__get_desktop_hint()

        theme = ''

        if desktop in ['kde']:
            pass

        elif desktop in ['gnome', 'mate', 'xfce']:
            try:
                import gi.repository.Gio
                settings = gi.repository.Gio.Settings('org.gnome.desktop.interface')
                font = settings.get_string('font-name')

                font_name, font_size = font.split(' ')
                theme = "<style type='text/css'>* { font-family: '%s'; }</style>" % (font_name)

            except:
                pass

        return theme

    @staticmethod
    def __get_toolkit(name, custom_toolkits, exact=False):
        #: defines the list of Lens backends to be preloaded for auto-detection
        __toolkits = {
            'gtk3':         ['lens.appgtk3',         'ViewGtk3'],
            'gtk':          ['lens.appgtk3',         'ViewGtk3'],
            'qt4':          ['lens.appqt4',          'ViewQt4'],
            'qt':           ['lens.appqt5webengine', 'ViewQt5WebEngine'],
            'qt5':          ['lens.appqt5webengine', 'ViewQt5WebEngine'],
            'qt5webengine': ['lens.appqt5webengine', 'ViewQt5WebEngine'],
            'qt5webkit':    ['lens.appqt5webkit',    'ViewQt5WebKit']
        }

        __toolkits.update(custom_toolkits)

        __tk_error = []

        if name in __toolkits:
            try:
                __tk = __toolkits[name]
                __module = __import__(__tk[0], globals(), locals(), [__tk[1]], 0)
                logger.debug('Loaded: {0}'.format(name))
                return getattr(__module, __tk[1], None)

            except:
                if exact:
                    raise Exception('Toolkit %s is not implemented or could not be loaded.' % (name))

                else:
                    logger.debug(traceback.format_exc())
                    __tk_error.append(name)

        for k in __toolkits:
            if k in __tk_error:
                continue

            try:
                logger.debug('Loading fallback: {0}'.format(k))
                __tk = __toolkits[k]
                __module = __import__(__tk[0], globals(), locals(), [__tk[1]], 0)
                return getattr(__module, __tk[1], None)
            except:
                logger.debug(traceback.format_exc())
                __tk_error.append(k)

        raise Exception('No fallback toolkits implemented or loaded.')

    def __load_toolkit(self, toolkit=None, toolkit_hint='gtk'):
        # determine the preferred toolkit to use and build the appropiate LensView
        if toolkit is None:
            toolkit = self.__get_desktop_toolkit_hint(toolkit_hint.lower())

        # attempt to load the preferred
        toolkit_klass = App.__get_toolkit(toolkit.lower(), self.custom_toolkits)
        logger.debug('Using {0} toolkit'.format(toolkit.lower()))

        self._lv = toolkit_klass(name=self._app_name, width=self._app_width, height=self._app_height, inspector=self._inspector, start_maximized=self._start_maximized)

        #: set system theme
        self._lv.set_system_theme(self.__get_desktop_theme())

        self._lv.set_uri_lens_base(self._uri_base + '/')

        logger.debug('Using lens data path: {0}'.format(self._uri_base))

        #: store an app reference to the thread manager
        self.threads = self._lv._manager

    def _dbus_async_cb(self, name):
        def decorator(*args, **kwargs):
            error = None

            # check for DBus exceptions
            if len(args) == 1 and isinstance(args[0], dbus.DBusException):
                error = args[0]

            self._lv.emit('dbus.'+name, error, *args)

        return decorator

    #
    # PROPERTIES

    @property
    def inspector(self):
        return self._inspector

    @inspector.setter
    def inspector(self, state):
        self._inspector = state

        # update window title on app name change
        self._lv.set_inspector(self._inspector)

    @property
    def name(self):
        return self._app_name

    @name.setter
    def name(self, name):
        self._app_name = name

        # update window title on app name change
        self._lv.set_title(self._app_name)

    #
    # PUBLIC METHODS

    def bind(self, name):
        """A decorator that is used to register a callback for
           a given signal. Example usage::

                 @app.connect('hello')
                 def hello_cb():
                     print("Hi!")

        :param name: the name of the signal to subscribe to
        """
        def decorator(f):
            self.on(name, f)
            return f

        return decorator

    def close(self):
        self._lv.close()

    # dbus helpers
    def dbus_async_call(self, signal, fn_method, *args):
        if not isinstance(fn_method, dbus.proxies._DeferredMethod) and \
             not isinstance(fn_method, dbus.proxies._ProxyMethod):
             raise Exception('Not a valid deferred/proxy method.')

        _cb = self._dbus_async_cb(signal)

        return fn_method(*args, reply_handler=_cb, error_handler=_cb)

    def dbus_interface(self, *args, **kwargs):
        return dbus.Interface(*args, **kwargs)

    def dbus_session(self):
        if self._dbus_session is None:
            self._dbus_session = dbus.SessionBus()

        return self._dbus_session

    def dbus_session_interface(self, org, path, interface=None):
        if interface is None:
            interface = org

        proxy = self.dbus_session().get_object(org, path)
        return self.dbus_interface(proxy, interface)

    def dbus_system(self):
        if self._dbus_system is None:
            self._dbus_system = dbus.SystemBus()

        return self._dbus_system

    def dbus_system_interface(self, org, path, interface=None):
        if interface is None:
            interface = org

        proxy = self.dbus_system().get_object(org, path)
        return self.dbus_interface(proxy, interface)

    def emit(self, name, *args):
        self._lv.emit_js(name, *args)

    def on(self, name, callback):
        self._lv.on(name, callback)

    def once(self, name, callback):
        self._lv.once(name, callback)

    def resize(self, width, height):
        """Resizes the application window.

        :param width: the requested width for the application window. If set to
                      `None`, the width won't be changed.
        :param height: the requested height for the application window. If set to
                       `None`, the height won't be changed.
        """
        if width is not None:
            self._app_width = width

        if height is not None:
            self._app_height = height

        self._lv.set_size(self._app_width, self._app_height)

    def set_title(self, title):
        self._lv.set_title(title)

    def signal(self, name, *args):
        self.emit(name, *args)

    def slot(self, name, callback):
        self.on(name, callback)

    def start(self, data=''):
        if len(data.strip()):
            logger.debug('Loading STRING: {0}'.format(data))

            self._lv.load_string(data)
            self._lv._run()
            sys.exit(0)

        else:
            #: validate app.html can be found
            for d in self.namespaces:
                _uri = os.path.abspath(os.path.join(d, 'app.html'))

                if os.path.exists(_uri):
                    logger.debug('Loading URI: {0}'.format(_uri))

                    self._lv.load_uri(_uri)
                    self._lv._run()
                    sys.exit(0)

                else:
                    logger.debug('URI entry point does not exist: {0}'.format(_uri))

        logger.error('Unable to load app.')
        exit(1)

    def toggle_window_maximize(self):
        self._lv.toggle_window_maximize()

    def toggle_window_fullscreen(self):
        self._lv.toggle_window_fullscreen()

