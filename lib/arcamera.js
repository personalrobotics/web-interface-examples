function ARCamera(basecam, options) {
  this._options = {pivotdist: 0.0};
  $.extend(this._options, options);

  this._cam = basecam;
  this._viewpos = new THREE.Vector3();
  this._theta = 0;
  this._phi = 0;
  this._rate = 0.05;
  this._minradius = 0.001;
  this._maxradius = 20.0;
  this._radius = 0.0;
  this._tarphi = 0.0;
  this._tartheta = 0.0;

  this.resetView();
}

function sphericalToCartesian(phi, theta, rad, offset) {

  var y = Math.sin(phi) * rad;
  var r2 = Math.cos(phi) * rad;
  var x = -Math.sin(theta) * r2;
  var z = Math.cos(theta) * r2;
  var ret = new THREE.Vector3(x, y, z);
  if(offset) {
    ret.add(offset);
  }
  return ret;
}

ARCamera.prototype.update = function() {
  this._theta += ( this._tartheta - this._theta ) * this._rate;
  this._phi   += ( this._tarphi - this._phi ) * this._rate;
  this._cam.position.copy(sphericalToCartesian(this._phi, this._theta, this._radius, this._viewpos));
  this._cam.lookAt( this._viewpos );
};

ARCamera.prototype.updateZoomDelta = function(dzoom) {
  this._radius = Math.max(this._minradius, Math.min(this._maxradius, this._radius + dzoom));
};

ARCamera.prototype.updateScreenDelta = function(dx, dy, sw, sh) {
  var dphi = ((dy / sh) * 1.0) * Math.PI;
  var dtheta = ((dx / sw) * 1.0) * Math.PI * 2.0;

  this._tartheta += dtheta;
  this._tarphi = Math.max(-Math.PI/2.0, Math.min(Math.PI/2.0, this._tarphi + dphi));
};

ARCamera.prototype.panScreenDelta = function(dx, dy, sw, sh) {
  var du = (dx / sw) * 2.0;
  var dv = (dy / sh) * 2.0;

  var ct = Math.cos(this._theta);
  var st = Math.sin(this._theta);

  var dx =   du * ct - dv * st;
  var dz =  -du * st - dv * ct;

  this._viewpos.x -= dx;
  this._viewpos.z += dz;
};

ARCamera.prototype.resetView = function() {
  this._viewpos.set(0.0, 0.0, -(this._options.pivotdist));
  this._radius = this._options.pivotdist;
  this._theta = 0.0;
  this._phi = 0.0;
};

ARCamera.prototype.setView = function(phi, theta, rad) {
  this._radius = rad;
  this._tarphi = phi;
  this._phi = this._tarphi;
  this._tartheta = theta;
  this._theta = this._tartheta;
}

var ocam;
var mouseDownState = false;
var mouseX = 0, mouseY = 0;
var prevMouseX = 0, prevMouseY = 0;
var mouseDX = 0, mouseDY = 0;

var zoomButtonDown = false;
var zoomButtonKeycode = 16; // shift
var panButtonDown = false;
var panButtonKeycode = 17; // ctrl


function initARCamera(rawcamera) {
  ocam = new ARCamera(rawcamera);

  document.addEventListener( 'mousedown', onCamMouseDown, false );
  document.addEventListener( 'mouseup', onCamMouseUp, false );
  document.addEventListener( 'mousemove', onCamDocumentMouseMove, false );
  document.addEventListener( 'keydown', onCamDocumentKeyDown, false );
  document.addEventListener( 'keyup', onCamDocumentKeyUp, false );
}

function updateARCamera() {
  mouseDX = mouseX - prevMouseX;
  mouseDY = mouseY - prevMouseY;
  prevMouseX = mouseX;
  prevMouseY = mouseY;

  if(mouseDownState == true) {
    ocam.updateScreenDelta(mouseDX, mouseDY, core.windowX, core.windowY);
  } else if(zoomButtonDown) {
    ocam.updateZoomDelta(mouseDY / 10.0);
  } else if(panButtonDown) {
    ocam.panScreenDelta(mouseDX, mouseDY, core.windowX, core.windowY);
  }

  ocam.update();
}

function onCamMouseDown() {
  mouseDownState = true;
}

function onCamMouseUp() {
  mouseDownState = false;
}

function onCamDocumentKeyDown(event) {
  if(event.keyCode == zoomButtonKeycode) {
    zoomButtonDown = true;
  }
  if(event.keyCode == panButtonKeycode) {
    panButtonDown = true;
  }
}

function onCamDocumentKeyUp(event) {
  if(event.keyCode == zoomButtonKeycode) {
    zoomButtonDown = false;
  }
  if(event.keyCode == panButtonKeycode) {
    panButtonDown = false;
  }
}

function onCamDocumentMouseMove( event ) {
  mouseX = event.clientX - core.windowHalfX;
  mouseY = event.clientY - core.windowHalfY;
}