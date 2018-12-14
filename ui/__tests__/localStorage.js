
var localStorageMock = (function () {
  var store = {};
  var jwt = require('jsonwebtoken');
  var token = jwt.sign({ foo: 'bar', exp: Math.floor(Date.now() / 1000) + 3000 }, 'shhhhh');

  var date = new Date();
  var d = new Date(date.getMilliseconds() + 100);

  store = {
    id_token: token,
    expires_at: d.getTime(),
    username: 'cbutler',
  };

  return {
    getItem(key) {
      return store[key];
    },
    setItem(key, value) {
      store[key] = value.toString();
    },
    clear() {
      store = {};
    },
    removeItem(key) {
      delete store[key];
    },
  };
}());

Object.defineProperty(window, 'localStorage', { value: localStorageMock });


var sessionStorageMock = (function () {
  var store = {};

  return {
    getItem(key) {
      return store[key];
    },
    setItem(key, value) {
      store[key] = value.toString();
    },
    clear() {
      store = {};
    },
    removeItem(key) {
      delete store[key];
    },
  };
}());

Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });
