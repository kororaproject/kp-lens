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
import signal
import threading
import time

from Lens.LensApp import LensApp
from Lens.LensView import LensView
from Lens.LensThread import LensThread, LensThreadManager

# GTK
from gi.repository import WebKit2, Gtk, GObject


class _GIdleObject(GObject.GObject):
  """
  Override gobject.GObject to always emit signals in the main thread
  by emmitting on an idle handler
  """
  def __init__(self):
    GObject.GObject.__init__(self)

  def emit(self, *args):
    GObject.idle_add(GObject.GObject.emit, self, *args)

class LensThreadGtk(threading.Thread, GObject.GObject):
  """
  Thread which uses GObject signals to return information
  to the GUI.
  """
  __gsignals__ = {
    "__lens":    (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (
      GObject.TYPE_STRING,
      GObject.TYPE_PYOBJECT,
    ))
  }

  def __init__(self, thread=None):
    threading.Thread.__init__(self)
    GObject.GObject.__init__(self)

    #TODO: type check
    self._uuid = thread.uuid
    self._lens_thread = thread

    self._lens_thread.on_any(self._thread_signal_cb)

  @property
  def uuid(self):
    return self._uuid

  def _thread_signal_cb(self, name, *args):
    self.emit('__lens', name, list(args))

  def run(self):
    if self._lens_thread is None:
      threading.Thread.run(self)
    else:
      self._lens_thread.run()

    self.emit('__lens', '__complete', [])



class LensThreadManagerGtk(LensThreadManager):
  """
  Manages many _GThreads. This involves starting and stopping
  said threads, and respecting a maximum num of concurrent threads limit
  """
  def __init__(self, maxConcurrentThreads=10):
    LensThreadManager.__init__(self, maxConcurrentThreads)

  def _add_thread(self, thread):
    _thread_gtk = LensThreadGtk(thread=thread)

    _thread_gtk.connect("__lens", self.__lens_cb)

    return _thread_gtk

  def _create_thread(self, completed_cb, progress_cb, user_data, target=None, *args, **kwargs):
    if isinstance(target, LensThread):
      thread = LensThreadGtk.fromLensThread(target)
    else:
      thread = LensThreadGtk(target=target, *args, **kwargs)

    # signals run in the order connected. Connect the user completed
    # callback first incase they wish to do something
    # before we delete the thread

    thread.connect("__lens", self.__lens_cb)

    return thread


  def __lens_cb(self, thread, name, args):
    if name == '__complete':
      self._thread_completed_cb(thread, *args)

    else:
      self.emit('__thread_%s_%s' % (name, thread.uuid), thread._lens_thread, *args)



class _WebView(WebKit2.WebView):
  """
  """

  __gsignals__ = {
    'on-js': (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_STRING,GObject.TYPE_PYOBJECT,))
  }

  def __init__(self):
    WebKit2.WebView.__init__(self)

    # register signals
    self.connect('context-menu', self._context_menu_cb)
    self.connect('decide-policy', self._decide_policy_cb)
    self.connect('load-changed', self._load_changed_cb)
    self.connect('notify::title', self._title_changed_cb)

    self.l_uri = None

    # disable right-click context menu
    try:
        self.get_settings().set_property('enable-accelerated-2d-canvas', True)
    except:
        pass
        # TODO: log failure to set

    try:
        self.get_settings().set_property('enable-smooth-scrolling', True)
    except:
        pass
        # TODO: log failure to set

    try:
        self.get_settings().set_property('enable_write_console_messages_to_stdout', True)
    except:
        pass
        # TODO: log failure to set

    try:
        self.get_settings().set_property('javascript-can-access-clipboard', True)
    except:
        pass
        # TODO: log failure to set

  def _context_menu_cb(self, view, context_menu, event, hit_test_result):
    return True

  def _decide_policy_cb(self, view, decision, decision_type):
    if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:

      # grab the requested URI
      uri = decision.get_request().get_uri()

  def _load_changed_cb(self, view, event):
    if event == WebKit2.LoadEvent.FINISHED:
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



class LensViewGtk(LensView):


  def __init__(self, name="MyLensApp", width=640, height=480, *args, **kwargs):
    LensView.__init__(self, name=name, width=width,height=height, *args, **kwargs)

    print(name)

    self._build_app()

  def _build_app(self):
    # build window and position in center of screen
    self._window = w = Gtk.Window()
    w.set_position(Gtk.WindowPosition.CENTER)

    # build webkit container
    self._lensview = lv = _WebView()

    # build scrolled window widget and add our appview container
    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    sw.add(lv)

    # build an autoexpanding box and add our scrolled window
    b = Gtk.VBox(homogeneous=False, spacing=0)
    b.pack_start(sw, expand=True, fill=True, padding=0)

    # add the box to the parent window and show
    w.add(b)

    # connect to Gtk signals
    lv.connect('on-js', self._on_js)
    w.connect('delete-event', self._delete_event_cb)

    # connect to Lens signals
    self.on('__close_app', self._close_cb)

    self.set_title(self._app_name)
    self.set_size(self._app_width, self._app_height)

    w.show_all()

  def _close_cb(self, *args):
    Gtk.main_quit(*args)

  def _delete_event_cb(self, *args):
    self.emit('__close_app', *args)

  def _run(self):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    Gtk.main()

  def emit_js(self, name, *args):
    self._lensview.run_javascript("var _rs = angular.element(document).scope(); _rs.safeApply(function(){_rs.$broadcast.apply(_rs,%s)});" % json.dumps([name] + list(args)), None, None, None)

  def load_uri(self, uri):
    print("Opening: %s" % uri)

    # load our index file
    self._lensview.load_uri(uri)

  def set_size(self, width, height):
    self._window.set_size_request(width, height)

  def set_title(self, title):
    self._window.set_title(title)
    self._window.set_wmclass(title, title)



class LensAppGtk(LensApp):


  def __init__(self, name="MyLensApp", width=640, height=480, *args, **kwargs):

    self._lv = LensViewGtk(name=name, width=width, height=height, *args, **kwargs)

    self.manager = LensThreadManagerGtk()

