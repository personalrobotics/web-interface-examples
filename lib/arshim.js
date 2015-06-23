WebVuforia = {};

WebVuforia.loadDataset = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 4;
	args = args.map(String);
	WebVuforiaNative.loadDataset.apply(WebVuforia, args);
};

WebVuforia.activateDataset = function() {
	var args = Array.prototype.slice.call(arguments);
	args.length = 3;
	args = args.map(String);
	WebVuforiaNative.activateDataset.apply(WebVuforia, args);
};

WebVuforia.deactivateDataset = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 3;
	args = args.map(String);
	WebVuforiaNative.deactivateDataset.apply(WebVuforia, args);
};

WebVuforia.unloadDataset = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 3;
	args = args.map(String);
	WebVuforiaNative.unloadDataset.apply(WebVuforia, args);
};

WebVuforia.onUpdate = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 1;
	args = args.map(String);
	WebVuforiaNative.onUpdate.apply(WebVuforia, args);
};

WebVuforia.onNfc = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 1;
	args = args.map(String);
	WebVuforiaNative.onNfc.apply(WebVuforia, args);
};

WebVuforia.takeScreenshot = function () {
	var args = Array.prototype.slice.call(arguments);
	args.length = 2;
	args = args.map(String);
	WebVuforiaNative.takeScreenshot.apply(WebVuforia, args);
};

WebVuforia.vuforiaAvailable = function() {
	return (typeof WebVuforiaNative != "undefined");
}

// Legacy rename to ARShim for Pyry since he refuses to refactor code.
ARShim = WebVuforia;