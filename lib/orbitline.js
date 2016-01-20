function Orbitline(options, shaderlibrary) {
	this.options = {
		vmult: 1.0,
		umult: 1.0,
		linewidth: 0.02,
		linetex: null,
		additive: false
	};
	$.extend(this.options, options);

	this._vecpts = [];
	this._shaderAttributes = {pivotPos: {type: "v3", value: []},
							  pivotDir: {type: "v3", value: []}, 
							  arcPos: {type: "f", value: []},
							  linecolor: {type: "v3", value: []}};
	this._npts = this.options.npts;
	this._vmult = this.options.vmult;
	this._umult = this.options.umult;
	this.buildGeometry();
	//this.updateGeometry(options.points);

	this._shaderUniforms = { 
								lineWidth: {type: "f", value: this.options.linewidth}, 
						    	diffuseColor: {type: "v4", value: new THREE.Vector4(1.0,0.0,0.0,1.0)}
						   };



	this._vshader = shaderlibrary.getShader("vs_line");
	
	if(this.options.linetex) {
		this._fshader = shaderlibrary.getShader("fs_uvline");
		this._shaderUniforms["hatchMap"] = {type: "t", value: this.options.linetex};
	} else {
		this._fshader = shaderlibrary.getShader("fs_line");
	}
	
	this._t = 0;

	// build material
	var shaderopts = {
        uniforms:       this._shaderUniforms,
        attributes:     this._shaderAttributes,
        vertexShader:   this._vshader,
        fragmentShader: this._fshader,
        //blending: 		THREE.AdditiveBlending,
        depthWrite: 	!(this.options.additive),
        depthTest:      true, 
        transparent:    this.options.additive, 
        side: THREE.DoubleSide
	};
	if(this.options.additive) {
		shaderopts.blending = THREE.AdditiveBlending;
	}

	this._shaderMaterial = new THREE.ShaderMaterial(shaderopts);

	this._vnode = new THREE.Mesh(this._geometry, this._shaderMaterial);
};

Orbitline.prototype.setLineWidth = function(linewidth) {
	this._shaderMaterial.uniforms.lineWidth.value = linewidth;
};

Orbitline.prototype.setLineColor = function(r, g, b) {
	this._shaderMaterial.uniforms.diffuseColor.value.set(r, g, b, 0.0);
};

Orbitline.prototype.setLineColorV = function(colorvec) {
	this._shaderMaterial.uniforms.diffuseColor.value.copy(colorvec);
};

Orbitline.prototype.setLineTexture = function(newtex) {
	this._shaderMaterial.uniforms.hatchMap.value = newtex;
};

Orbitline.prototype.getNode = function() {
	return this.getTHREENode();
};

Orbitline.prototype.getTHREENode = function() {
	return this._vnode;
};

Orbitline.prototype.getTHREEMat = function() {
	return this._shaderMaterial;
};

function vecListToArrayList(veclist) {
	var ret = [];
	for(var i = 0; i < veclist.length; ++i) {
		ret.push(veclist[i].toArray());
	}
	return ret;
}

Orbitline.prototype.updateGeometry = function(newpts, newcolors) {
	if(newpts.length != this._npts) {
		console.log("Point number mismatch for fancy line: expected " + newpts.length + ", got: "
			+ this._npts);
		// TODO: make this do something more sensible like fill the remainder with zeros
		return;
	};

	// convert everything to three vectors
	var vecpts = this._vecpts;
	var ntoadd = (newpts.length - vecpts.length);
	for(var i = 0; i < ntoadd; ++i) {
		vecpts.push(new THREE.Vector3(0.0,0.0,0.0));
	}

	//console.log("newptslen: "+newpts.length);
	//console.log("vecptslen: "+vecpts.length);

	for(var i = 0; i < newpts.length; ++i) {
		//console.log("newptsi: " + newpts[i]);
		//console.log("vecptsi: " + vecpts[i]);
		vecpts[i].fromArray(newpts[i]);
	};

	var pivotDirs = this._shaderAttributes.pivotDir.value;
	var pivotPoses = this._shaderAttributes.pivotPos.value;
	var arcPoses = this._shaderAttributes.arcPos.value;
	var colorVals = this._shaderAttributes.linecolor.value;

	// The slightly less pretty way of choosing the pivot directions:
	// just use the direction of the next link
	// TODO: use average of previous+next links	

	var arcpos = 0;
	for(var i = 1; i < this._npts; ++i) {
		var p0 = vecpts[i-1];
		var p1 = vecpts[i];
		pivotDirs[2*i+0].subVectors(p0, p1);
		pivotDirs[2*i+1].subVectors(p1, p0);
		pivotPoses[2*i+0].copy(p1);
		pivotPoses[2*i+1].copy(p1);
		arcpos += (pivotDirs[2*i+0].length() * this._vmult);
		arcPoses[2*i+0] = arcpos;
		arcPoses[2*i+1] = arcpos;

		if(newcolors) {
			colorVals[2*i+0].copy(newcolors[i]);
			colorVals[2*i+1].copy(newcolors[i]);
		}
	};
	// deal specially with first point
	pivotDirs[0].copy(pivotDirs[2]);
	pivotDirs[1].copy(pivotDirs[3]);
	pivotPoses[0].copy(vecpts[0]);
	pivotPoses[1].copy(vecpts[0]);

	this._shaderAttributes.pivotDir.needsUpdate = true;
	this._shaderAttributes.pivotPos.needsUpdate = true;
	this._shaderAttributes.arcPos.needsUpdate = true;
	if(newcolors) {
		this._shaderAttributes.linecolor.needsUpdate = true;
	}
};

function makeColorGradient(c0, c1, npts) {
	
}

Orbitline.prototype.buildGeometry = function() {
	var npts = this._npts;
	console.log("Building a line with " + npts + "points.");
	var posList = this._shaderAttributes.pivotPos.value;
	var dirList = this._shaderAttributes.pivotDir.value;
	var arcList = this._shaderAttributes.arcPos.value;
	var colorList = this._shaderAttributes.linecolor.value;
	this._geometry = new THREE.Geometry();

	var uv0 = new THREE.Vector3(0.0,0.0);
	var uv1 = new THREE.Vector3(0.0,this._umult);
	var face_uv0 = [uv0, uv1, uv1];
	var face_uv1 = [uv0, uv1, uv0];
	var tval = 0.5;

	// generate 2n vertices
	for (var i = 0; i < npts; ++i ) {
		var vertex0 = new THREE.Vector3();
		// TODO: initialize these in some better way
		// (create random vertices in a big sphere to try to 
		//  force the view-frustum culling to always draw the line)
		vertex0.x = Math.random() * 1000 - 500.0;
		vertex0.y = Math.random() * 1000 - 500.0;
		vertex0.z = Math.random() * 1000 - 500.0;
		var vertex1 = vertex0.clone();
		vertex1.y = 1.0;

		this._geometry.vertices.push( vertex0 );
		this._geometry.vertices.push( vertex1 );
		posList.push(new THREE.Vector3(0,1,0));
		posList.push(new THREE.Vector3(0,1,0));
		dirList.push(new THREE.Vector3(0,1,0));
		dirList.push(new THREE.Vector3(0,1,0));
		arcList.push(i);
		arcList.push(i);

		tval = 1.0; //1.0 - (i / npts);

		// colorList.push(new THREE.Vector3(tval, tval, tval));
		// colorList.push(new THREE.Vector3(tval, tval, tval));
		colorList.push(new THREE.Vector3(0.6, 0.8, 1));
		colorList.push(new THREE.Vector3(0.6, 0.8, 1));
	}

	// generate 2(n-1) faces
	// don't worry about normals
	for (var i = 0; i < npts-1; ++i) {
		var v0 = i*2;
		var v1 = v0 + 1;
		var v2 = v0 + 2;
		var v3 = v0 + 3;

		var face0 = new THREE.Face3( v0, v1, v3 );
		var face1 = new THREE.Face3( v0, v3, v2 );
		this._geometry.faces.push(face0);
		this._geometry.faces.push(face1);
		this._geometry.faceVertexUvs[0].push(face_uv0);
		this._geometry.faceVertexUvs[0].push(face_uv1);
	}
};


Orbitline.prototype.setVisible = function(visible) {
	this._vnode.visible = visible;	
};

Orbitline.prototype.setPosition = function(x, y, z) {
	this._vnode.position.set(x, y, z);
};