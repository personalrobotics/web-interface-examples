function ShaderLibrary(baseurl) {
	this.baseurl = baseurl;
	this.shaders = {};
	this.numpending = 0;
	this.onAllLoaded = null;
}

function shaderLoaded(jqXHR, textStatus) {
	this.shaderlib.setShaderText(this.name, jqXHR.responseText);
}

ShaderLibrary.prototype.setLoadCallback = function(f) {
	this.onAllLoaded = f;
};

ShaderLibrary.prototype.setShaderText = function(shadername, shadertext) {
	this.shaders[shadername].data = shadertext;
	this.shaders[shadername].loaded = true;
	--(this.numpending);
	console.log("Loaded shader " + shadername + "; " + this.numpending + " pending shaders.");
	if(this.numpending <= 0 && this.onAllLoaded != null) {
		this.onAllLoaded();
	}
};

ShaderLibrary.prototype.loadShaders = function() {
	// first, count how many we need to load
	// (do this first to avoid possible synchronization issues)
	// (i.e., if it manages to load a shader before the loop completes)
	this.numpending = 0;
	for(shadername in this.shaders) {
		if(this.shaders[shadername].loaded == false) {
			++(this.numpending);
		}
	}

	for(shadername in this.shaders) {
		if(!this.shaders[shadername].loaded) {
			$.ajax({
				url: this.shaders[shadername].url,
				dataType: 'text',
				context: {
					name: shadername,
					shaderlib: this
				},
				complete: shaderLoaded
			});
		}
	}

	console.log("Trying to load " + this.numpending + " shaders.");
};

ShaderLibrary.prototype.getShader = function(shadername) {
	if(shadername in this.shaders) {
		if(this.shaders[shadername].loaded) {
			return this.shaders[shadername].data;
		} else {
			console.log("Shader " + shadername + " not loaded yet!");
			return null;
		}
	} else {
		console.log("Shader " + shadername + " doesn't exist!");
		return null;
	}
};

ShaderLibrary.prototype.addShader = function(shadername, shaderurl) {
	console.log("Adding shader " + shadername);
	this.shaders[shadername] = {loaded: false, data: "", url: this.baseurl + shaderurl};
}