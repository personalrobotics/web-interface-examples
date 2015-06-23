function BaseGrid(gridw, gridh, gridspacing) {
	this.w = gridw;
	this.h = gridh;
	this.spacing = gridspacing;
	this.cspacing = gridspacing;
	this.circleres = 80;
	this.linemat = new THREE.LineBasicMaterial({color: 0xaaaaaa});
	this.subnodes = [];
}

BaseGrid.prototype.setVisibility = function(vstate) {
	console.log("Setting base grid visiblity to " + vstate);
	//this.node.visible = vstate;
	for(var i = 0; i < this.subnodes.length; ++i) {
		this.subnodes[i].visible = vstate;
	}
};

BaseGrid.prototype.createCircle = function(radius, thetares) {
	var dtheta = Math.PI * 2.0 / thetares;
	var geometry = new THREE.Geometry();
	for (var i = 0; i < thetares; ++i ) {
		var vertex = new THREE.Vector3();
		vertex.x = Math.cos(dtheta*i) * radius;
		vertex.z = Math.sin(dtheta*i) * radius;
		vertex.y = 0.0;
		geometry.vertices.push( vertex );
	}
	// add last point again to complete circle
	var finalv = new THREE.Vector3();
	finalv.copy(geometry.vertices[0]);
	geometry.vertices.push(finalv);
	var circle = new THREE.Line(geometry, this.linemat, THREE.LineStrip);
	return circle;
};

BaseGrid.prototype.createSpacedLines = function(width, length, forward, right, spacing) {
	var npts = Math.floor(length / spacing);
	var geometry = new THREE.Geometry();
	for(var i = 0; i < npts+1; ++i) {
		var fv = new THREE.Vector3();
		fv.copy(forward);
		fv.multiplyScalar(i * spacing - length/2.0);
		var rv = new THREE.Vector3();
		rv.copy(right);
		rv.multiplyScalar(width / 2.0);
		var pt0 = new THREE.Vector3();
		pt0.addVectors(fv, rv);
		var pt1 = new THREE.Vector3();
		pt1.subVectors(fv, rv);
		geometry.vertices.push(pt0);
		geometry.vertices.push(pt1);
	}
	var line = new THREE.Line(geometry, this.linemat, THREE.LinePieces);
	return line;
}

BaseGrid.prototype.buildNode = function() {
	var basenode = new THREE.Object3D();
	var fv = new THREE.Vector3(1.0,0.0,0.0);
	var rv = new THREE.Vector3(0.0,0.0,1.0);
	var lines1 = this.createSpacedLines(this.w, this.h, fv, rv, this.spacing);
	var lines2 = this.createSpacedLines(this.h, this.w, rv, fv, this.spacing);
	basenode.add(lines1);
	this.subnodes.push(lines1);
	basenode.add(lines2);
	this.subnodes.push(lines2);
	for(var i = 0; i < Math.floor(Math.min(this.w,this.h)/2.0/this.cspacing)+1; ++i) {
		var curcircle = this.createCircle(i*this.cspacing, this.circleres);
		basenode.add(curcircle);
		this.subnodes.push(curcircle);
	}
	this.node = basenode;
};

BaseGrid.prototype.addToScene = function(scene) {
	this.buildNode();
	scene.add(this.node);
};