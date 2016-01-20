function FoodAnnotation(options) {
	this._options = {
		centralsize: 0.1,
		shaderlib: null,
		parent: null,
		centraltex: null,
	};
	$.extend(this._options, options);

	// other setup here

	this._build();

	this._x = 0;
	this._y = 0;
	this._rad = 0;
	this._theta = 0;
	this.active = false;

	this._data = {
		x: 0,
		y: 0,
		rad: 0,
		theta: 0,
		label: "UNKNOWN"
	}
}

FoodAnnotation.prototype.getNode = function() {
	return this._node;
};

FoodAnnotation.prototype.setActive = function(activestate) {
	this._node.visible = activestate;
	this.active = activestate;
};

FoodAnnotation.prototype._updateRingRad = function(newrad) {
	var pts = this._ringpts;
	var npts = pts.length;

	var dt = 2.0 * Math.PI / (npts - 1);
	for(var i = 0; i < npts; ++i) {
		var theta = dt * i;
		pts[i] = [Math.cos(theta) * newrad, 0.0, Math.sin(theta) * newrad];
	}

	this._ring.updateGeometry(pts);
};

FoodAnnotation.prototype._build = function() {
	this._node = new THREE.Object3D();
	if(this._options.parent) {
		this._options.parent.add(this._node);
	}

	var opts = {npts: 20, 
			  linewidth: 0.01, 
			  linetex: null,
			  vmult: 10.0,
			  umult: 0.1,
			  radius: 1.0};
	$.extend(opts, this._options);

	var pathLine = new Orbitline(opts, this._options.shaderlib);

	this._ringpts = [];
	for(var i = 0; i < opts.npts; ++i) {
		this._ringpts.push([0,0,0]);
	}

	this._ring = pathLine;

	this._updateRingRad(1.0);

	this._node.add(pathLine.getTHREENode());

	var planegeo = new THREE.PlaneGeometry( this._options.centralsize, this._options.centralsize );
	var planemat = new THREE.MeshBasicMaterial( {map: this._options.centraltex, color: 0xff0000, side: THREE.DoubleSide, alphaTest: 0.5} );
	this._plane = new THREE.Mesh( planegeo, planemat );
	this._plane.rotation.x = -Math.PI / 2.0;
	this._node.add(this._plane);
	this._mat = planemat;
};

FoodAnnotation.prototype.setImage = function(newtex, texlabel) {
	this._mat.map = newtex;
	this._data.label = texlabel;
};

FoodAnnotation.prototype.updatePosition = function(x, y, imx, imy) {
	this._data.x = x;
	this._data.y = y;
	this._data.imx = imx;
	this._data.imy = imy;
	this._node.position.set(x, 0.01, y);
};

// Update radius and facing direction according to a 'drag' from the center
// of (dx, dy)
FoodAnnotation.prototype.updateParams = function(dx, dy, imdx, imdy) {
	//console.log("Updating params: " + dx + ", " + dy);

	this._data.rad = Math.sqrt(dx*dx + dy*dy);
	this._data.imrad = Math.sqrt(imdx*imdx + imdy*imdy);
	this._data.theta = Math.atan2(-dy, dx) - Math.PI / 2.0;
	this._plane.rotation.z = this._data.theta;
	this._updateRingRad(this._data.rad);
};

FoodAnnotation.prototype.getData = function() {
	return this._data;
};

function FoodAnnotationSet(options) {
	this._options = {
		stabtex: null,
		scooptex: null,
		camera: null,
		plane: null
	};
	$.extend(this._options, options);

	this._annotations = [];
	this._selectedAnnotation = null;
	this._mode = "ADD";

	this._textures = {
		"SCOOP": this._options.scooptex,
		"STAB": this._options.stabtex
	}
	this._annotype = "STAB";
	this._annotex = this._textures[this._annotype];

	this._raycaster = new THREE.Raycaster();
	this._camera = this._options.camera;
	this._plane = this._options.plane;

	this._mouseDownPos = new THREE.Vector3();
	this._imMouseDownPos = new THREE.Vector3();
}

FoodAnnotationSet.prototype.clear = function() {
	// don't actually delete anything, just hide them
	this._annotations.forEach(function(a){a.setActive(false)});
};

// Delete clicked annotations
FoodAnnotationSet.prototype.deleteAnnotation = function(x, y) {
	this._annotations.forEach(function(ca){
		var dx = x - ca._data.x;
		var dy = y - ca._data.y;
		if(Math.sqrt(dx*dx + dy*dy) < ca._data.rad) {
			ca.setActive(false);
		}
	});
};

FoodAnnotationSet.prototype.getAnnotations = function() {
	var annotationdata = [];
	for(var i = 0; i < this._annotations.length; ++i) {
		if(this._annotations[i].active) {
			annotationdata.push(this._annotations[i].getData());
		}
	}
	return annotationdata;
};

FoodAnnotationSet.prototype._createNewAnnotation = function() {
	var opts = {
		// put options here
	};
	$.extend(opts, this._options);
	var foodannotation = new FoodAnnotation(opts);
	foodannotation.setActive(true);
	return foodannotation;
};

FoodAnnotationSet.prototype._addAnnotation = function() {
	// first, see if there's an inactive annotation we can use
	for(var i = 0; i < this._annotations.length; ++i) {
		if(!(this._annotations[i].active)) {
			this._annotations[i].setActive(true);
			return this._annotations[i];
		}
	}

	// otherwise, add a new annotation
	var newanno = this._createNewAnnotation();
	this._annotations.push(newanno);
	return newanno;
};

FoodAnnotationSet.prototype.mouseDown = function(x, y, imx, imy) {
	var cpos = this._projectClickToPlane(x, y);
	if(!cpos) {
		return;
	}
	this._mouseDownPos.copy(cpos);
	this._imMouseDownPos.set(imx, imy, 0);

	if(this._mode === "ADD") {
		console.log("Adding new annotation...");
		var newanno = this._addAnnotation();
		newanno.updatePosition(cpos.x, cpos.z, imx, imy);
		newanno.setImage(this._annotex, this._annotype);
		this._selectedAnnotation = newanno;
		this._mousedown = true;
	} else if(this._mode === "DELETE") {
		this.deleteAnnotation(cpos.x, cpos.z);
	}
	this._mousedown = true;
};

FoodAnnotationSet.prototype.mouseUp = function() {
	this._mousedown = false;
	this._selectedAnnotation = null;
};

FoodAnnotationSet.prototype.mouseMove = function(x, y, imx, imy) {
	var cpos = this._projectClickToPlane(x, y);
	if(!cpos) {
		return;
	}

	if(this._mode === "ADD" && this._mousedown && this._selectedAnnotation != null) {
		var dpos = new THREE.Vector3();
		var imdpos = new THREE.Vector3();
		dpos.subVectors(cpos, this._mouseDownPos);
		imdpos.subVectors(new THREE.Vector3(imx, imy, 0), this._imMouseDownPos);

		this._selectedAnnotation.updateParams(dpos.x, dpos.z, imdpos.x, imdpos.y);
	}
};

FoodAnnotationSet.prototype._projectClickToPlane = function(clickx, clicky) {
	var ndx = clickx * 2.0 - 1.0; // scale from [0,1] --> [-1,1]
	var ndy = -(clicky * 2.0 - 1.0);

	this._raycaster.setFromCamera( new THREE.Vector2(ndx,ndy), this._camera );

	var intersects = this._raycaster.intersectObject( this._plane, false );
	if(intersects.length > 0) {
		return intersects[0].point;
	} else {
		return null;
	}
}

FoodAnnotationSet.prototype.setMode = function(newmode) {
	this._mode = newmode;
};

FoodAnnotationSet.prototype.setAnnotationType = function(annotype) {
	this._annotype = annotype;
	this._annotex = this._textures[annotype];
};

function Cycler(options) {
	this._options = options;
	this._idx = 0;
}

Cycler.prototype.curOption = function() {
	return this._options[this._idx];
};

Cycler.prototype.nextOption = function() {
	this._idx = (this._idx + 1) % this._options.length;
	return this._options[this._idx];
};