function ARCore(options) {
	this.options = {usestats: true,
					usegrid: true,
					gridsize: 2.0,
					gridspacing: 0.1,
					createlights: true,
					fov: 40.0,
					shaderpath: "shaders/",
					markerxml: null,
					markerdat: null,
					shaders: [],
					canvas: null,
					width: null,
					height: null
					};
	$.extend(this.options, options);

	this.initcallback = null;
	this.updatecallback = null;

	this.cameraLocked = false;
}

ARCore.prototype.onWindowResize = function() {
	this.windowX = this.options.width || window.innerWidth;
	this.windowY = this.options.height || window.innerHeight;
	this.windowHalfX = this.windowX / 2.0;
	this.windowHalfY = this.windowY / 2.0;
	console.log("WX: " + this.windowX + ", WY: " + this.windowY);

	this.camera.aspect = this.windowX / this.windowY;
	this.camera.updateProjectionMatrix();

	this.renderer.setSize( this.windowX, this.windowY );
}


ARCore.prototype.addDefaultLights = function() {
	// add some lights so we can see stuff
	this.scene.add( new THREE.AmbientLight( 0xcccccc ) );

	var directionalLight = new THREE.DirectionalLight( 0xeeeeee );
	directionalLight.position.x = Math.random() - 0.5;
	directionalLight.position.y = Math.random() - 0.5;
	directionalLight.position.z = Math.random() - 0.5;
	directionalLight.position.normalize();
	this.scene.add( directionalLight );

	// var pointLight = new THREE.PointLight( 0xffffff, 4 );
	// this.scene.add(pointLight);
};

ARCore.prototype.init = function() {
	var newthis = this;

	this.usingVuforia = false;

	if(this.options.canvas != null) {
		this.renderer = new THREE.WebGLRenderer({canvas: this.options.canvas, alpha: true});
		this.renderer.setClearColor(0x000000, 0);
	} else {
		this.renderer = new THREE.WebGLRenderer();
	}
	this.renderer.setSize( this.options.width || window.innerWidth, this.options.height || window.innerHeight );
	document.body.appendChild( this.renderer.domElement );

	if(this.options.usestats) {
		this.stats = new Stats();
		this.stats.domElement.style.position = 'absolute';
		this.stats.domElement.style.top = '0px';
		document.body.appendChild( this.stats.domElement );
	} else {
		this.stats = null;
	}

	this.camera = new THREE.PerspectiveCamera( this.options.fov, window.innerWidth / window.innerHeight, 0.1, 100 );
	this.onWindowResize();
	this.scene = new THREE.Scene();

	initARCamera(this.camera);

	this.root = new THREE.Object3D();
	this.scene.add(this.root);

	this.frameManager = new FrameManager({});
	this.root.add(this.frameManager._root);

	window.addEventListener( 'resize', function(){
		newthis.onWindowResize();
	}, false );

	if(this.options.createlights) {
		this.addDefaultLights();
	}

	if(this.options.usegrid) {
		this.grid = new BaseGrid(this.options.gridsize,
								 this.options.gridsize,
								 this.options.gridspacing);
		this.grid.addToScene(this.root);
	}

	this.shaderlib = new ShaderLibrary(this.options.shaderpath);
	this.shaderlib.setLoadCallback(function() {
		newthis.shadersLoaded();
	});

	var curshader;
	for(var i = 0; i < this.options.shaders.length; ++i) {
		curshader = this.options.shaders[i];
		this.shaderlib.addShader(curshader[0], curshader[1]);
	}
	this.shaderlib.loadShaders();

	//init_ws();
};

ARCore.prototype.shadersLoaded = function() {
	console.log("Shaders loaded!");
	this.finalInit();
}

ARCore.prototype.finalInit = function() {
	if(this.initcallback) {
		this.initcallback(this);
	}

	if(this.options.markerxml && this.options.markerdat) {
		this.usingVuforia = init_vuforia(this.options.markerxml, this.options.markerdat);
	}

	this.animate();
}

ARCore.prototype.updateCamera = function() {
	if(!this.cameraLocked) {
		updateARCamera();
	}
};

ARCore.prototype.animate = function() {

	if(this.updatecallback) {
		this.updatecallback();
	}

	var newthis = this;
	requestAnimationFrame( function() {
		newthis.animate();
	} );

	if(!this.usingVuforia) {
		this.updateCamera();
	}
	this.renderer.render(this.scene, this.camera);

	if(this.stats) {
		this.stats.update();
	}
}