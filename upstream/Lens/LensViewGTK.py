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
import pprint

from Lens import LensView

# GTK
from gi.repository import WebKit2, Gtk, GObject

class LensViewWebKitGTK(WebKit2.WebView):
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
      # push config on every page load
      #self._push_config()
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


class LensViewGTK(LensView.LensView):
  def __init__(self, *args, **kwargs):
    LensView.LensView.__init__(self, *args, **kwargs)

    self._app_name = kwargs.get('name', 'Unknown')

    self._build_app()

  def _build_app(self):
    # build window
    w = Gtk.Window()
    w.set_position(Gtk.WindowPosition.CENTER)
    w.set_wmclass(self._app_name, self._app_name)
    w.set_title(self._app_name)
    w.set_size_request(792, 496)

    # build webkit container
    lv = LensViewWebKitGTK()

    # XXX: Move to AppView
    lv.connect('on-js', self._onJS)

    # build scrolled window widget and add our appview container
    sw = Gtk.ScrolledWindow()
    sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    sw.add(lv)

    # build an autoexpanding box and add our scrolled window
    b = Gtk.VBox(homogeneous=False, spacing=0)
    b.pack_start(sw, expand=True, fill=True, padding=0)

    # add the box to the parent window and show
    w.add(b)
    w.connect('delete-event', self._delete_event_cb)
    w.show_all()

    self._window = w
    self._lensView = lv


    # connect the Lens specific close event
    self.on('__close_app', self._close_cb)

  def _delete_event_cb(self, *args):
    self.emit('__close_app', *args)

  def _close_cb(self, *args):
    Gtk.main_quit(*args)


  #
  # emitJS and onJS are the primary entry and exit points for the python/javascript bridge
  def emitJS(self, signal, message={}):
    self._lensView.run_javascript("var _rs = angular.element(document).scope(); _rs.$apply( function() { _rs.$broadcast('%s', %s) });" % (signal, json.dumps(message)), None, None, None)

  def loadURI(self, uri):
    print("Opening: %s" % uri)

    # load our index file
    self._lensView.load_uri(uri)


