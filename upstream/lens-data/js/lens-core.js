window.lens = {
  "__cb":{},
  "__cb_once":{},
  "__emit":function(data) {
    if (data.length > 0) {
      var name = data[0];
      var args = data.slice(1);

      s = window.lens.__cb[name] || [];

      gs = window.lens.__cb['__*'] || [];

      so = window.lens.__cb_once[name] || [];
      delete window.lens.__cb_once[name];

      s.forEach(function(cb) { cb.apply(undefined, args); });
      so.forEach(function(cb) { cb.apply(undefined, args); });
      gs.forEach(function(cb) { cb.apply(undefined, data); });
    }
  },
  "emit":function() {
    var _args = Array.prototype.slice.call(arguments);

    if (_args.length > 0) {
      var c = {name: _args.shift(), args: _args};

      /* update document title */
      var t = document.title;
      document.title = '_BR::' + JSON.stringify(c);
      document.title = t;
    }
  },
  "has_subscribers":function(name) {
    s = window.lens.__cb[name] || [];
    so = window.lens.__cb_once[name] || [];

    return s.length + so.length;
  },
  "on":function(name, cb) {
    window.lens.__cb[name] = window.lens.__cb[name] || [];
    window.lens.__cb[name].push(cb);
  },
  "on_any":function(cb) {
    window.lens.__cb['__*'] = window.lens.__cb['__*'] || [];
    window.lens.__cb['__*'].push(cb);
  },
  "once":function(name, cb) {
    window.lens.__cb_once[name] = window.lens.__cb[name] || [];
    window.lens.__cb_once[name].push(cb);
  }
};
