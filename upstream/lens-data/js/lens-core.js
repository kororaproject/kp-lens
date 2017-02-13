window.lens = window.lens || {};
window.lens.__cb = window.lens.__cb || {};
window.lens.__cb_once = window.lens.__cb_once || {};
window.lens.__broadcast = window.lens.__broadcast || function(name, args) {
  var s = window.lens.__cb[name] || [];
  Array.prototype.push.apply(s, window.lens.__cb['*']       || []);
  Array.prototype.push.apply(s, window.lens.__cb_once[name] || []);
  delete window.lens.__cb_once[name];

  var data = args || [];
  data.unshift(name);

  s.forEach(function(cb) { cb.apply(undefined, data); });
};
window.lens.__emit = window.lens.__emit || function(data) {
  if (data.length > 0) {
    var name = data[0];
    var args = data.slice(1);

    window.lens.__broadcast(name, args)
  }
};
window.lens.emit = window.lens.emit || function() {
  var args = Array.prototype.slice.call(arguments);

  if (args.length > 0) {
    document.title = '_BR::' + JSON.stringify({
      "name":args.shift(),
      "args":args
    });
    document.title = '';
  }
};
window.lens.has_subscribers = window.lens.has_subscribers || function(name) {
  var s  = window.lens.__cb[name] || [];
  var so = window.lens.__cb_once[name] || [];

  return s.length + so.length;
};
window.lens.on = window.lens.on || function(name, cb) {
  var getType = {};
  // assume "on any" when only callback is supplied
  if (name && getType.toString.call(name) === '[object Function]') {
    window.lens.__cb['*'] = window.lens.__cb['*'] || [];
    window.lens.__cb['*'].push(name);
  }
  else if (cb && getType.toString.call(cb) === '[object Function]') {
    window.lens.__cb[name] = window.lens.__cb[name] || [];
    window.lens.__cb[name].push(cb);
  }
};
window.lens.once = window.lens.once || function(name, cb) {
  if (cb && getType.toString.call(cb) === '[object Function]') {
    window.lens.__cb_once[name] = window.lens.__cb[name] || [];
    window.lens.__cb_once[name].push(cb);
  }
};
