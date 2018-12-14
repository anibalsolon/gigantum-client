
var fetch = require('isomorphic-fetch');
var FormData = require('form-data');
require('raf/polyfill');

var { configure } = require('enzyme');
var Adapter = require('enzyme-adapter-react-16');

configure({ adapter: new Adapter() });
// need to add root to JSDOM for mounting react

// set variables for the api
window.location.hostname = 'localhost';
window.location.protocol = 'https:';

// window.location.assign.mockClear();
// window.location.assign('https://localhost:10000');
var document = window.document;

var newDiv = document.createElement('div');
newDiv.setAttribute('id', 'root');
// set for proxy
process.env.GIGANTUM_API = process.env.USE_PROXY ? ':10010/api/labbook/' : ':10000/api/labbook/';

// add document globally
global.document = window.document;

// add window globally
global.window = window;

global.window.resizeTo = function (width, height) {
  global.window.innerWidth = width || global.window.innerWidth;
  global.window.innerHeight = width || global.window.innerHeight;
  global.window.dispatchEvent(new Event('resize'));
};

// add node fetch for environment
global.fetch = fetch;

// add formdata api for multipart forms
global.FormData = FormData;

// add file api for uploads
global.File = window.File;

global.window.matchMedia = window.matchMedia || function () { return { matches: false, addListener: () => {}, removeListener: () => {} }; };

global.requestAnimationFrame = function (callback) {
  setTimeout(callback, 0);
};

(function () {
    var lastTime = 0;
    var vendors = ['ms', 'moz', 'webkit', 'o'];
    // for (var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
    //     window.requestAnimationFrame = window[vendors[x] + 'RequestAnimationFrame'];
    //     window.cancelAnimationFrame = window[vendors[x] + 'CancelAnimationFrame']
    //                                || window[vendors[x] + 'CancelRequestAnimationFrame'];
    // }

    for (var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
        window.requestAnimationFrame = window[`${vendors[x]}${RequestAnimationFrame}`];
        window.cancelAnimationFrame = window[`${vendors[x]}${CancelAnimationFrame}`]
                                   || window[`${vendors[x]}${CancelRequestAnimationFrame}`];
    }

    if (!window.requestAnimationFrame) {
        window.requestAnimationFrame = (callback, element) => {
            var currTime = new Date().getTime();
            var timeToCall = Math.max(0, 16 - (currTime - lastTime));
            var id = window.setTimeout(
              () => {
                var time = currTime + timeToCall;
                callback(time);
              },
              timeToCall,
            );
            lastTime = currTime + timeToCall;
            return id;
        };
     }

    if (!window.cancelAnimationFrame) {
        window.cancelAnimationFrame = function (id) {
            clearTimeout(id);
        };
    }
}());

// const oneHundredSeconds = 1 * 1000 * 100
// // set timout to one hundred seconds
// jasmine.DEFAULT_TIMEOUT_INTERVAL = oneHundredSeconds

// export default () => global;
