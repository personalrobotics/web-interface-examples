function FrameManager(options) {
  this._options = {};
  $.extend(this._options, options);
  this._root = new THREE.Object3D();
  this.frames = {};
  this.fiducials = {};
  this._dummyscale = new THREE.Vector3();
}

FrameManager.prototype.addFrame = function(name) {
  if(this.frames[name]) {
    console.warn("Cannot addFrame: frame [" + name + "] already exists!");
    return this.frames[name];
  }

  var newframe = new THREE.Object3D();

  this.frames[name] = newframe;
  this._root.add(newframe);

  return newframe;
};

FrameManager.prototype.setFiducial = function(name, posemat) {
  this.fiducials[name] = posemat;
};

FrameManager.prototype.setFiducialEuler = function(name, rx, ry, rz, tx, ty, tz) {
  var fpos = new THREE.Matrix4();
  var fq = new THREE.Quaternion();
  fq.setFromEuler(new THREE.Euler(rx, ry, rz));
  var fp = new THREE.Vector3(tx, ty, tz);
  fpos.compose(fp, fq, new THREE.Vector3(1.0, 1.0, 1.0));

  this.setFiducial(name, fpos);
};

// addFiducial is just an alias for setFiducial
FrameManager.prototype.addFiducial = FrameManager.prototype.setFiducial;

// Set a frame's pose from another object in world-space
FrameManager.prototype.setFramePoseFromObject = function(framename, object) {
  var src = this.frames[framename];
  if(!src) {
    console.error("Frame [" + framename + "] does not exist!");
    return;
  }
  var mdest = new THREE.Matrix4();
  mdest.copy(object.matrixWorld);
  mdest.decompose(src.position, src.quaternion, this._dummyscale);
};

// Set a frame's pose from its observation of a fiducial
FrameManager.prototype.setFramePoseFromFiducial = function(framename, fidname, observedFidPose) {
  var src = this.frames[framename];
  if(!src) {
    console.error("Frame [" + framename + "] does not exist!");
    return;
  }
  var fidpose = this.fiducials[fidname];
  if(!fidpose) {
    console.error("Fiducial [" + fidname + "] does not exist!");
    return;
  }

  // want to find M_frame so that
  // M_frame * Fid_observed = Fid_world
  // (thus M_frame = Fid_world * Fid_observed^-1)
  var mdest = new THREE.Matrix4();
  var inverseMat = new THREE.Matrix4();
  inverseMat.getInverse(observedFidPose);
  mdest.multiplyMatrices(fidpose, inverseMat);

  mdest.decompose(src.position, src.quaternion, this._dummyscale);
};