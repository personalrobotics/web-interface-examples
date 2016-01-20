var current_tracking_data = {};
var vuforia_xml = "";

function onVFLoad(bla) {
	console.log("Loaded!");
	// Activate the halloween dataset (note the two callbacks in strings, for success and failure).
	ARApi.activateDataset(vuforia_xml, onVFError, onVFError);
	console.log("Activated!");
}

function vfu_real(vfdata) {
	current_tracking_data = unpackVuforiaData(vfdata);
}

function onVFUpdate(vuforiaData) {
	vfu_real(vuforiaData);
}

function onVFError(errstuff) {
	console.log(errstuff);	
}

function init_vuforia(datasetxml, datasetdat) {
	// Load the halloween dataset (note the two callbacks in strings, for success and failure).

	if(WebVuforia.loadDataset) {
		ARApi = WebVuforia;
		console.log("WebVuforia seems to be populated.");
	} else {
		ARApi = ARShim;
		console.log("Something is broken-- using ARShim instead of WebVuforia");
	}

	if(!WebVuforia.vuforiaAvailable()) {
		console.log("Vuforia not available.");
		return false;
	}

	vuforia_xml = datasetxml;

	var ld = ARApi.loadDataset;
	console.log(ld);

	console.log("Loading dataset...");
	ARApi.loadDataset(datasetxml, datasetdat, onVFLoad, onVFError);
	console.log("Called load.");

	// Set the update callback to a function in a string.
	ARApi.onUpdate(onVFUpdate);

	return true;
}

function unpackVFTransform(vftf) {
	var a = vftf;
	var rtemp = new THREE.Matrix4();
	rtemp.set(-a[1], -a[0],  -a[2], 0,
	 		   a[5], a[4],  a[6], 0,
	 		   a[9], a[8], a[10], 0,
	 		     0,    0,    0,   1);
	//target.rotation.setFromRotationMatrix(rtemp);
	var ptemp = new THREE.Vector3(a[3], -a[7], -a[11]);
	//console.log(ptemp);
	//target.position.copy(ptemp);
	return {rotation: rtemp, position: ptemp};
}

function unpackVuforiaData(vfdata) {
	var ret = {};
	for(var i = 0; i < vfdata.length; ++i) {
		ret[vfdata[i].name] = unpackVFTransform(vfdata[i].pose);
	}
	return ret;
}