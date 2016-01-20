var core;
var linetex, linetex2;
var selset;
var agrabber;
var jgrabber;
var artag = "herb_target";
var cursor_path;
var multiArmature;
var liveArmature;
var curtraj, trajlength;
var t = 0.0;
var headrotator;
var vuforiaFudgeFactor = 1.0;

var annoset;

var tempsphere, tempsphere2;

var foodplane, foodplanemat;

var stabtex, scooptex;

var bodyframe;

var modecycler, motioncycler;

function startInit() {
	linetex = THREE.ImageUtils.loadTexture( 'images/white.png' );
	linetex.wrapS = linetex.wrapT = THREE.RepeatWrapping;

	linetex2 = THREE.ImageUtils.loadTexture( 'images/stab.png' );
	linetex2.wrapS = linetex2.wrapT = THREE.RepeatWrapping;

	stabtex = THREE.ImageUtils.loadTexture( 'images/stab.png' );
	scooptex = THREE.ImageUtils.loadTexture( 'images/scoop.png' );

	var shaders = 	[["vs_line", 			"vs_screenline.txt"],
					 ["fs_line", 			"fs_solid.txt"],
					 ["fs_uvline", 			"fs_uvline_tint.txt"]];

	var bname = "http://" + window.location.hostname + ":8080/database/";
	var xmlpath = bname + "herbtarget.xml"; 
	var datpath = bname + "herbtarget.dat";

	core = new ARCore({shaders: shaders,
					   markerxml: xmlpath,
					   markerdat: datpath,
					   width: 1280,
					   height: 720,
					   fov: 90.0,
					   canvas: $("#render-canvas")[0]});
	core.initcallback = finishInit;
	core.updatecallback = appupdate;
	core.init();
}

var planetex = null;
function finishInit() {
	var fpos = new THREE.Matrix4();
	var fp = new THREE.Vector3(0.0, 0.0, 0.0);
	var fq = new THREE.Quaternion();
	fq.setFromEuler(new THREE.Euler(Math.PI / 2.0, 0.0, 0.0));
	fpos.compose(fp, fq, new THREE.Vector3(1.0, 1.0, 1.0));

	var fpos2 = new THREE.Matrix4();
	var fp2 = new THREE.Vector3(0.0, 0.0, 0.0);
	var fq2 = new THREE.Quaternion();
	fq2.setFromEuler(new THREE.Euler(Math.PI / 2.0, 0.0, 0.0));
	fpos2.compose(fp2, fq2, new THREE.Vector3(1.0, 1.0, 1.0));

	vuforiaFudgeFactor = 0.85;

	var p2 = Math.PI / 2.0;
	core.frameManager.addFiducial(artag, fpos2);
	core.frameManager.setFiducialEuler("herb_target", p2, 0, p2*-1, 0.14, -0.08, 0.0);

	var testo = new THREE.Quaternion();
	testo.setFromEuler(new THREE.Euler(Math.PI / 3.0, 0.0, 0.0));


	var camframe = core.frameManager.addFrame("camera");
	bodyframe = core.frameManager.addFrame("body");
	//bodyframe.rotation.x = -Math.PI / 2.0;

	document.addEventListener( 'mousedown', onMouseDown, false );
	document.addEventListener( 'mouseup', onMouseUp, false );
	document.addEventListener( 'mousemove', onMouseMove, false );

	tempsphere = new THREE.Mesh(new THREE.SphereGeometry(0.02, 100, 100), new THREE.MeshNormalMaterial());
	tempsphere.position.set(0,0,0);
	bodyframe.add(tempsphere);

	tempsphere2 = new THREE.Mesh(new THREE.SphereGeometry(0.02, 100, 100), new THREE.MeshNormalMaterial());
	tempsphere2.position.set(0,0,0);
	bodyframe.add(tempsphere2);

	var planegeo = new THREE.PlaneGeometry( 10, 10 );
	// //THREE.ImageUtils.crossOrigin = '';
	// //$("#food-video-stream")[0].crossOrigin = "*";
	// //$("#food-video-stream")[0].setAttribute('crossorigin', 'anonymous');
	// planetex = new THREE.Texture($("#food-video-stream")[0]);
	foodplanemat = new THREE.MeshBasicMaterial( {color: 0x808080, side: THREE.DoubleSide} );
	foodplane = new THREE.Mesh( planegeo, foodplanemat );
	foodplane.rotation.x = Math.PI / 2.0;
	foodplane.position.y = -0.01;
	bodyframe.add(foodplane);
	foodplane.visible = false;

	annoset = new FoodAnnotationSet({
		stabtex: stabtex,
		scooptex: scooptex,
		camera: core.camera,
		plane: foodplane,
		shaderlib: core.shaderlib,
		centralsize: 0.1,
		parent: bodyframe,
		centraltex: scooptex,
		npts: 30,
		linetex: linetex
	});

	modecycler = new Cycler(["ADD", "DELETE"]);
	motioncycler = new Cycler(["SCOOP", "STAB"]);

	setMode(modecycler.curOption());
	setMotion(motioncycler.curOption());

	$("#modebutton").click(function(e){
		e.stopPropagation();
		setMode(modecycler.nextOption());
		console.log("Mode button");
	});

	$("#resetbutton").click(function(e){
		e.stopPropagation();
		annoset.clear();
	});

	$("#motionbutton").click(function(e){
		e.stopPropagation();
		setMotion(motioncycler.nextOption());
	});

	$("#submitbutton").click(function(e){
		e.stopPropagation();
		submitAnnotations();
	});

	$("#camerabutton").click(function(e){
		e.stopPropagation();
		setCameraMode(!(core.cameraLocked));
	});

	// stop click on these from also creating annotations
	$("#modebutton").mousedown(stopBubble);
	$("#resetbutton").mousedown(stopBubble);
	$("#motionbutton").mousedown(stopBubble);
	$("#submitbutton").mousedown(stopBubble);

    // playing an mjpeg stream is no more complicated than just
    // creating (or setting) an image with its URL
    var mjpegURL = "http://ada:8080/stream?topic=/ueye_XS/image_color";
    $("#food-video-stream").attr("src", mjpegURL);

    core.cameraLocked = true;
    ocam.setView(Math.PI / 2.0, 0.0, 0.5);
    updateARCamera();

    initRos();
}

var ros = null, sendTopic = null;
var sendTopicName = "/webui/clicks"
var rosbridgeServerUrl = "ws://ada:9090";

// publish a click as a space-separated plain-text pair
// e.g.: "123 928"
function publishDataString(datastring) {
    console.log("Publishing: " + datastring);

    var rosmsg = new ROSLIB.Message({
        data: datastring
    });

    sendTopic.publish(rosmsg);
}

function initRos() {
    ros = new ROSLIB.Ros({
        url : rosbridgeServerUrl
    });
   
    ros.on('connection', function() {
        console.log('Connected to websocket server.');

        sendTopic = new ROSLIB.Topic({
        	ros : ros,
        	name : sendTopicName,
        	messageType : 'std_msgs/String'
    	});
    });
   
    ros.on('error', function(error) {
        console.log('Error connecting to websocket server: ', error);
    });
   
    ros.on('close', function() {
        console.log('Connection to websocket server closed.');
    });
}

function stopBubble(e) {
	console.log("Trying to stop bubbling");
	e.stopPropagation();
}

function setMode(modeval) {
	$("#modebutton").text("Mode: " + modeval);
	annoset.setMode(modeval);
}

function setMotion(motionval) {
	$("#motionbutton").text("Motion: " + motionval);
	annoset.setAnnotationType(motionval);
}

function submitAnnotations() {
	var annos = annoset.getAnnotations();
	var annojson = JSON.stringify(annos);
	console.log("Submitting annotations...");
	console.log(annojson);
	publishDataString(annojson);
}

function updateAR() {
	if(artag in current_tracking_data) {
		var p = current_tracking_data[artag].position;
		var p_s = new THREE.Vector3();
		p_s.copy(p);
		p_s.multiplyScalar(vuforiaFudgeFactor);
		var rmat = current_tracking_data[artag].rotation;
		var tmat = new THREE.Matrix4();
		tmat.copy(rmat);
		tmat.setPosition(p_s);

		core.frameManager.setFramePoseFromFiducial("camera",
													artag,
													tmat);

		core.camera.position.copy(core.frameManager.frames["camera"].position);
		core.camera.quaternion.copy(core.frameManager.frames["camera"].quaternion);

		//console.log("Setting stuff: " + tmat);
	}
}

function onMouseDown(event) {
	if(!core.cameraLocked) {
		return;
	}

	var sMX = event.clientX / core.windowX;
	var sMY = event.clientY / core.windowY;

	if(annoset) {
		annoset.mouseDown(sMX, sMY, event.clientX, event.clientY);
	}
}

function onMouseUp(event) {
	if(annoset) {
		annoset.mouseUp();
	}
}

function onMouseMove(event) {
	if(!core.cameraLocked) {
		return;
	}

	var sMX = event.clientX / core.windowX;
	var sMY = event.clientY / core.windowY;

	if(annoset) {
		annoset.mouseMove(sMX, sMY, event.clientX, event.clientY);
	}
}

function appupdate() {
	t += 1.0;
	if(t > 100.0) {
		t = 0.0;
	}

	if(t < 5.0) {
		//planetex.needsUpdate = true;
	}

	// var tempx = Math.cos(t * 3.0) * 1;
	// var tempy = Math.sin(t * 2.0) * 1;
	// tempsphere2.position.set(tempx, 0, tempy);
	// if(foodannotation) {
	// 	foodannotation.updateParams(tempx, tempy);
	// }

	if(core.usingVuforia) {
		updateAR();
	}
}

$(function() {
	startInit();
});