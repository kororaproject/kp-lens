window.lens = {
  "__cb":{},
  "__cb_once":{},
  "__emit":function(data) {
    if (data.length > 0) {
      var name = data[0];
      var args = data.slice(1);

      s = window.lens.__cb[name] || [];
      Array.prototype.push.apply(s, window.lens.__cb['__*']     || []);
      Array.prototype.push.apply(s, window.lens.__cb_once[name] || []);
      delete window.lens.__cb_once[name];

      s.forEach(function(cb) { cb.apply(undefined, args); });
    }
  },
  "emit":function() {
    var args = Array.prototype.slice.call(arguments);

    if (args.length > 0) {
      document.title = '_BR::' + JSON.stringify({
        "name":args.shift(),
        "args":args
      });
    }
  },
  "has_subscribers":function(name) {
    s  = window.lens.__cb[name] || [];
    so = window.lens.__cb_once[name] || [];

    return s.length + so.length;
  },
  "on":function(name, cb) {
    var getType = {};
    // assume "on any" when only callback is supplied
    if (name && getType.toString.call(name) === '[object Function]') {
      window.lens.__cb['__*'] = window.lens.__cb['__*'] || [];
      window.lens.__cb['__*'].push(name);
    }
    else if (cb && getType.toString.call(cb) === '[object Function]') {
      window.lens.__cb[name] = window.lens.__cb[name] || [];
      window.lens.__cb[name].push(cb);
    }
  },
  "once":function(name, cb) {
    if (cb && getType.toString.call(cb) === '[object Function]') {
      window.lens.__cb_once[name] = window.lens.__cb[name] || [];
      window.lens.__cb_once[name].push(cb);
    }
  }
};
